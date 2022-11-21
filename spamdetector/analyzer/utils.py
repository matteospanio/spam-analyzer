from enum import Enum
import re
import requests
import datetime
import spamdetector.analyzer.data_structures as ds


class Regex(Enum):
    DOMAIN = re.compile(r"([\-A-Za-z0-9]+\.)+[A-Za-z]{2,6}")
    IP = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    MAILTO = re.compile(r"mailto:(\w+@\w+\.\w+)(\?subject=(.+))?")
    HTTP_LINK = re.compile(r'(http://([A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.&=\?]*)?)')
    HTTPS_LINK = re.compile(r'(https://([A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.&=\?]*)?)')
    SHORT_LINK = re.compile(r'(([A-Za-z0-9]+\.)+[A-Za-z]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.=&\?]*)?)')
    GAPPY_WORDS = re.compile(r'([A-Za-z0-9]+(<!--*-->|\*|\-))+')
    HTML_FORM = re.compile(r'<form')
    HTML_TAG = re.compile(r'<[^>]+>')


def inspect_headers(headers: dict, wordlist):
    """A detailed analysis of the email headers

    Args:
        headers (dict): a dictionary containing parsed email headers
        wordlist (list[str]): a list of words to be used as a spam filter in the subject field

    Returns:
        tuple: a tuple containing all the results of the analysis

    - has_spf (bool): True if the email has a SPF record
    - has_dkim (bool): True if the email has a DKIM record
    - has_dmarc (bool): True if the email has a DMARC record
    - domain_matches (bool): True if the domain of the sender matches the domain of the server
    - has_auth_warning (bool): True if the email has an authentication warning
    - has_suspect_words (bool): True if the email has gappy words or forbidden words in the subject
    - send_year (int): the year in which the email was sent (in future versions should be a datetime object)
    """
    has_spf = spf_pass(headers)
    has_dkim = dkim_pass(headers)
    has_dmarc = dmarc_pass(headers)
    domain_matches = from_domain_matches_received(headers)
    auth_warn = has_auth_warning(headers)
    has_suspect_subject, subject_is_uppercase = analyze_subject(headers, wordlist)
    send_date, _ = parse_date(headers)

    return (has_spf, has_dkim, has_dmarc, domain_matches, auth_warn, has_suspect_subject, subject_is_uppercase, send_date)

def spf_pass(headers: dict) -> bool:
    """Checks if the email has a SPF record

    Args:
        headers (dict): a dictionary containing parsed email headers

    Returns:
        bool: True if the email has a SPF record
    """
    spf = headers.get('Received-SPF') or headers.get('Authentication-Results') or headers.get('Authentication-results')
    if spf is not None and 'pass' in spf.lower():
        return True
    return False

def dkim_pass(headers: dict) -> bool:
    """Checks if the email has a DKIM record

    Args:
        headers (dict): a dictionary containing parsed email headers

    Returns:
        bool: True if the email has a DKIM record
    """
    if headers.get('DKIM-Signature') is not None:
        return True
    dkim = headers.get('Authentication-Results') or headers.get('Authentication-results')
    if dkim is not None and 'dkim=pass' in dkim.lower():
        return True
    return False

def dmarc_pass(headers: dict) -> bool:
    """Checks if the email has a DMARC record

    Args:
        headers (dict): a dictionary containing parsed email headers

    Returns:
        bool: True if the email has a DMARC record
    """
    dmarc = headers.get('Authentication-Results') or headers.get('Authentication-results')
    if dmarc is not None and 'dmarc=pass' in dmarc.lower():
        return True
    return False

def has_auth_warning(headers: dict) -> bool:
    """Checks if the email has an authentication warning

    Args:
        headers (dict): a dictionary containing parsed email headers

    Returns:
        bool: True if the email has an authentication warning
    """
    if headers.get('X-Authentication-Warning') is not None:
        return True
    return False

def analyze_subject(headers: dict, wordlist) -> tuple[bool, bool]:
    """Checks if the email has gappy words or forbidden words in the subject

    Args:
        headers (dict): a dictionary containing parsed email headers
        wordlist (list[str]): a list of words to be used as a spam filter in the subject field
    """
    subject: str = headers.get('Subject')
    if subject is not None:
        matches = Regex.GAPPY_WORDS.value.search(subject)
        if matches is not None:
            return True, subject.isupper()

    for word in wordlist:
        if word in subject:
            return True, subject.isupper()
    return False, False

def is_valid_tz(date: datetime.datetime):
    try:
        return -12 < int(date.utcoffset().__str__().split(':')[0]) < 14
    except Exception:
        return -12 < int(date.tzinfo.__str__().split(':')[0].replace('UTC', '')) < 14

def parse_date(headers: dict) -> tuple[datetime.datetime | None, bool]:
    """Date format should follow RFC 2822, this function expects a date in the format: "Wed, 21 Oct 2015 07:28:00 -0700",
    and returns a tuple where:
    1. the first element is the parsed date or `None` if the date is not in the correct format
    2. the second element is a boolean indicating if the date is valid or not

    Eventually in future versions will be specified the kind of error that occurred, like in spamassassin (e.g. "invalid date", "absurd tz", "future date")

    """
    date = headers.get('Date')

    # truncate at newline characters
    date = date.splitlines()[0]
    
    # parse date
    try:
        parsed_date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
        return (parsed_date, True)
    except Exception:
        return (date, False)

def from_domain_matches_received(headers: dict) -> bool:
    email_domain = get_domain(headers.get('From'))
    server_domain = get_domain(headers.get('Received'))

    return ( email_domain == server_domain )

def get_domain(field: str):
    """Extracts the domain from a field

    Args:
        field (str): a string expected to contain a domain

    Returns:
        Domain: a Domain object containing the domain name and the TLD
    """
    # TODO: should take in consideration only the string before 'by word'

    if 'unknown' in field:
        return ds.Domain('unknown')

    domain_match = Regex.DOMAIN.value.search(field)

    if domain_match:
        domain_name = field[domain_match.start():domain_match.end()]
        return ds.Domain(domain_name)
    else:
        ip_match = Regex.IP.value.search(field)
        if ip_match:
            ip_address = field[ip_match.start():ip_match.end()]
            return ds.Domain.from_ip(ip_address)

    return ds.Domain('unknown')

def inspect_body(body, wordlist, domain):
    """
    A detailed analysis of the email body
    
    Args:
        body (str): the body of the email
        wordlist (list[str]): a list of words to be used as a spam filter in the body
        domain (Domain): the domain of the sender
        
    Returns:
        tuple: a tuple containing the following information:
        
    - has_http_links (bool): True if the email has http links
    - has_script (bool): True if the email has script tags or javascript code
    - forbidden_words_percentage (float): the percentage of forbidden words in the body
    - has_form (bool): True if the email has a form
    - contains_html (bool): True if the email contains html tags
    
    """
    body = body.lower()
    has_links, has_mailto, https_only = check_links(body)
    has_script = has_script_tag(body)
    forbidden_words_percentage = percentage_of_bad_words(body, wordlist)
    has_form = has_html_form(body)
    contains_html = has_html(body)

    return (has_links, has_mailto, https_only, has_script, forbidden_words_percentage, has_form, contains_html)
    
def has_html(body):
    """Checks if the email contains html tags

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email contains html tags
    """
    return True if Regex.HTML_TAG.value.search(body) else False


def has_html_form(body) -> bool:
    """Checks if the email has a form

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email has a form
    """
    return True if Regex.HTML_FORM.value.search(body) else False

def percentage_of_bad_words(body, wordlist) -> float:
    """Calculates the percentage of forbidden words in the body

    Args:
        body (str): the body of the email
        wordlist (list[str]): a list of words to be used as a spam filter in the body

    Returns:
        float: the percentage of forbidden words in the body
    """
    bad_words = 0
    for word in wordlist:
        if word in body:
            bad_words += len(word.split(' '))
    return bad_words / len(body.split(' '))

def get_body_links(body) -> list[str]:
    links = []

    http = Regex.HTTP_LINK.value.findall(body)
    https = Regex.HTTPS_LINK.value.findall(body)
    mailto = Regex.MAILTO.value.findall(body)

    if http == [] and https == [] and mailto == []:
        not_http = Regex.SHORT_LINK.value.findall(body)
        links = [link[0] for link in not_http]

    for link in http:
        if 'www.w3.org' not in link[0]:
            links.append(link[0])
    for link in https:
        if 'spamassassin' not in link[0]:
            links.append(link[0])

    return links

def has_mailto_links(body) -> bool:
    """Checks if the email has mailto links

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email has mailto links
    """
    return True if Regex.MAILTO.value.search(body) else False

def check_links(body):
    links = get_body_links(body)

    return (links != []), has_mailto_links(body), https_only(links)

def has_inactive_links(links) -> bool:
    for link in links:
        if not is_active(link):
            return True
    return False

def is_active(link) -> bool:
    # FIXME: it slows down the process
    #        it check if it returns a 200 status code not only if the link is active
    """Checks if a link is active"""
    if 'https' and 'http' not in link:
        link = 'http://' + link

    try:
        response = requests.get(link, timeout=5)
        return (True, response.status_code)
    except Exception:
        return (False, 0)

def https_only(links: list[str]) -> bool:
    for link in links:
        if 'https://' not in link:
            return False
    if links == []:
        return False
    return True

def has_script_tag(body) -> bool:
    """Checks if the email has script tags or javascript code

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email has script tags or javascript code
    """
    unsecure_tags = ['<script>', '</script>', 'onload', 'onerror']
    for tag in unsecure_tags:
        if tag in body:
            return True
    return False

def inspect_attachments(attachments: list):
    has_attachments = len(attachments) > 0
    is_executable = False
    for attachment in attachments:
        a_type = attachment.get('mail_content_type')
        if a_type == 'application/octet-stream':
            is_executable = True
    return (has_attachments, is_executable)

def inspect_spamassassin(headers):
    if headers.get('X-Spam-Flag') is not None:
        return "Spam"
    return "Ham"
    