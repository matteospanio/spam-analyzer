import re
from enum import Enum
from typing import List, Literal, Union

from bs4 import BeautifulSoup
from mailparser import MailParser

from spamanalyzer.date import Date
from spamanalyzer.domain import Domain


class Regex(Enum):
    DOMAIN = re.compile(r"([\-A-Za-z0-9]+\.)+[A-Za-z]{2,6}")
    IP = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    MAILTO = re.compile(r"mailto:(\w+@\w+\.\w+)(\?subject=(.+))?")
    HTTP_LINK = re.compile(
        r"(http://([A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.&=\?]*)?)"
    )
    HTTPS_LINK = re.compile(
        r"(https://([A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.&=\?]*)?)"
    )
    SHORT_LINK = re.compile(
        r"(([A-Za-z0-9]+\.)+[A-Za-z]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.=&\?]*)?)")
    GAPPY_WORDS = re.compile(r"([A-Za-z0-9]+(<!--*-->|\*|\-))+")
    HTML_FORM = re.compile(r"<\s*form", re.DOTALL)
    HTML_TAG = re.compile(r"<[^>]+>")
    HTML_PAIR_TAG = re.compile(r"<\s*(\w+)[^>]*>(.*?)<\s*/\s*\1\s*>", re.DOTALL)
    IMAGE_TAG = re.compile(r"<\s*img", re.DOTALL)


async def inspect_headers(email: MailParser, wordlist):
    """A detailed analysis of the email headers.

    Args:
        headers (dict): a dictionary containing parsed email headers
        wordlist (list[str]): a list of words to be used as a spam filter in the
        subject field

    Returns:
        tuple: a tuple containing all the results of the analysis

    - has_spf (bool): True if the email has a SPF record
    - has_dkim (bool): True if the email has a DKIM record
    - has_dmarc (bool): True if the email has a DMARC record
    - domain_matches (bool): True if the domain of the sender matches the domain of
      the server
    - has_auth_warning (bool): True if the email has an authentication warning
    - has_suspect_words (bool): True if the email has gappy words or forbidden words
      in the subject
    - send_year (int): the year in which the email was sent (in future versions should
      be a datetime object)

    """

    headers = email.headers

    has_suspect_subject, subject_is_uppercase = analyze_subject(headers, wordlist)
    send_date = parse_date(headers, email.timezone)
    received_date = parse_date(email.received[0], email.timezone)

    return {
        "has_spf": spf_pass(headers),
        "has_dkim": dkim_pass(headers),
        "has_dmarc": dmarc_pass(headers),
        "domain_matches": await from_domain_matches_received(email),
        "auth_warn": has_auth_warning(headers),
        "has_suspect_subject": has_suspect_subject,
        "subject_is_uppercase": subject_is_uppercase,
        "received_date": received_date,
        "send_date": send_date,
    }


def spf_pass(headers: dict) -> bool:
    """Checks if the email has a SPF record."""
    spf = (headers.get("Received-SPF") or headers.get("Authentication-Results")
           or headers.get("Authentication-results"))
    if spf is not None and "pass" in spf.lower():
        return True
    return False


def dkim_pass(headers: dict) -> bool:
    """Checks if the email has a DKIM record."""
    if headers.get("DKIM-Signature") is not None:
        return True
    dkim = headers.get("Authentication-Results") or headers.get(
        "Authentication-results")
    if dkim is not None and "dkim=pass" in dkim.lower():
        return True
    return False


def dmarc_pass(headers: dict) -> bool:
    """Checks if the email has a DMARC record."""
    dmarc = headers.get("Authentication-Results") or headers.get(
        "Authentication-results")
    if dmarc is not None and "dmarc=pass" in dmarc.lower():
        return True
    return False


def has_auth_warning(headers: dict) -> bool:
    """Checks if the email has an authentication warning, usually it means that
    the sender claimed to be someone else."""
    if headers.get("X-Authentication-Warning") is not None:
        return True
    return False


def analyze_subject(headers: dict, wordlist) -> tuple[bool, bool]:
    """Checks if the email has gappy words or forbidden words in the subject.

    Args:
        headers (dict): a dictionary containing parsed email headers
        wordlist (list[str]): a list of words to be used as a spam filter in the subject
        field

    """
    subject: str = headers.get("Subject")  # type: ignore
    if subject is not None:
        matches = Regex.GAPPY_WORDS.value.search(subject)
        if matches is not None:
            return True, subject.isupper()

        for word in wordlist:
            if word in subject:
                return True, subject.isupper()

        return False, subject.isupper()

    return False, False


def parse_date(headers: dict, timezone: Union[str, Literal[0]]):
    """Date format should follow RFC 2822, this function expects a date in the format:
    "Wed, 21 Oct 2015 07:28:00 -0700", and returns a tuple where:
    1. the first element is the parsed date or `None` if the date is not in the correct
      format
    2. the second element is a boolean indicating if the date is valid or not

    Eventually in future versions will be specified the kind of error that occurred,
    like in spamassassin (e.g. "invalid date", "absurd tz", "future date")

    """
    date = headers.get("Date") or headers.get("date_utc")

    if date is None:
        return None

    # truncate at newline characters
    date = date.splitlines()[0]

    # parse date
    return Date(date, tz=int(float(timezone)))


async def from_domain_matches_received(email: MailParser) -> bool:
    email_domain = await get_domain(email.headers.get("From"))  # type: ignore
    try:
        server_domain = await get_domain(email.received[0].get("from"))
    except Exception:
        # server_domain = get_domain(email.received[0].get('by'))
        server_domain = await get_domain("unknown")

    return email_domain == server_domain


async def get_domain(field: str):
    """Extracts the domain from a field.

    Args:
        field (str): a string expected to contain a domain

    Returns:
        Domain: a Domain object containing the domain name and the TLD

    """
    # TODO: should take in consideration only the string before 'by word'

    if "unknown" in field:
        return Domain("unknown")

    domain_match = Regex.DOMAIN.value.search(field)

    if domain_match:
        domain_name = field[domain_match.start():domain_match.end()]
        return Domain(domain_name)

    ip_match = Regex.IP.value.search(field)
    if ip_match:
        ip_address = field[ip_match.start():ip_match.end()]
        return await Domain.from_ip(ip_address)

    return Domain("unknown")


def inspect_body(body: str, wordlist, domain):
    """A detailed analysis of the email body.

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
    from textblob import TextBlob  # FIXME: moved here for testing purposes

    is_uppercase = is_upper(body)
    body = body.lower()
    link_list = get_links_from_str(body)
    links = check_links(body)
    has_form = has_html_form(body)
    contains_html = has_html(body)

    if links["has_links"]:
        for link in link_list:
            body = body.replace(link, "")

    if contains_html:
        parsed_body = parse_html(body)
        blob = TextBlob(parsed_body)
        forbidden_words_percentage = percentage_of_bad_words(parsed_body, wordlist)
    else:
        blob = TextBlob(body)
        forbidden_words_percentage = percentage_of_bad_words(body, wordlist)

    return {
        "has_links": links["has_links"],
        "has_mailto": links["mailto"],
        "has_images": has_images(body),
        "https_only": links["https_only"],
        "text_polarity": blob.sentiment.polarity,  # type: ignore
        "text_subjectivity": blob.sentiment.subjectivity,  # type: ignore
        "contains_script": has_script_tag(body),
        "is_uppercase": is_uppercase,
        "forbidden_words_percentage": forbidden_words_percentage,
        "contains_form": has_form,
        "contains_html": contains_html,
    }


def is_upper(body: str) -> bool:
    if body == "" or body is None:
        return False
    count = 0
    word_list = body.split()
    if len(word_list) <= 0:
        return False
    for word in word_list:
        if word.isupper():
            count += 1
    return count / len(word_list) > 0.6


def parse_html(body: str) -> str:
    soup = BeautifulSoup(body, "html.parser")
    return soup.get_text()


def has_html(body: str) -> bool:
    """Checks if the email contains html tags.

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email contains html tags

    """
    return bool(Regex.HTML_TAG.value.search(body)) or bool(
        Regex.HTML_PAIR_TAG.value.search(body))


def has_images(body: str) -> bool:
    """Checks if the email contains images.

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email contains images

    """
    return bool(Regex.IMAGE_TAG.value.search(body))


def has_html_form(body: str) -> bool:
    """Checks if the email has a form.

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email has a form

    """
    return bool(Regex.HTML_FORM.value.search(body))


def percentage_of_bad_words(body: str, wordlist: List[str]) -> float:
    """Calculates the percentage of forbidden words in the body.

    Args:
        body (str): the body of the email
        wordlist (list[str]): a list of words to be used as a spam filter in the body

    Returns:
        float: the percentage of forbidden words in the body

    """
    bad_words = 0
    for word in wordlist:
        if word in body:
            bad_words += len(word.split(" "))
    return bad_words / len(body.split(" "))


def get_links_from_str(body: str) -> List[str]:
    links = []

    http = Regex.HTTP_LINK.value.findall(body)
    https = Regex.HTTPS_LINK.value.findall(body)
    mailto = Regex.MAILTO.value.findall(body)

    if http == [] and https == [] and mailto == []:
        not_http = Regex.SHORT_LINK.value.findall(body)
        links = [link[0] for link in not_http]

    for link in http:
        if "www.w3.org" not in link[0]:
            links.append(link[0])
    for link in https:
        if "spamassassin" not in link[0]:
            links.append(link[0])

    return links


def has_mailto_links(body) -> bool:
    """Checks if the email has mailto links.

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email has mailto links

    """
    return bool(Regex.MAILTO.value.search(body))


def check_links(body):
    links = get_links_from_str(body)

    return {
        "has_links": links != [],
        "mailto": has_mailto_links(body),
        "https_only": https_only(links),
    }


def https_only(links: List[str]) -> bool:
    if links == []:
        return False

    for link in links:
        if "https://" not in link:
            return False
    return True


def has_script_tag(body: str) -> bool:
    """Checks if the email has script tags or javascript code.

    Args:
        body (str): the body of the email

    Returns:
        bool: True if the email has script tags or javascript code

    """
    unsecure_tags = ["<script>", "</script>", "onload", "onerror"]
    for tag in unsecure_tags:
        if tag in body:
            return True
    return False


def inspect_attachments(attachments: List) -> dict:
    """A detailed analysis of the email attachments.

    Args:
        attachments (List):  a list of attachments

    Returns:
        dict: a dictionary containing the following information:

        ```python
        {
            "has_attachments": bool,         # True if the email has attachments
            "attachment_is_executable": bool # True if the email has
                                             # an attachment in executable format
        }

    """
    has_attachments = len(attachments) > 0
    is_executable = False
    for attachment in attachments:
        a_type = attachment.get("mail_content_type")
        if a_type == "application/octet-stream":
            is_executable = True
    return {
        "has_attachments": has_attachments,
        "attachment_is_executable": is_executable,
    }
