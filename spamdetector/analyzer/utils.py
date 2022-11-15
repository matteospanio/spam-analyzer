from enum import Enum
import re
import spamdetector.analyzer.data_structures as ds


class Regex(Enum):
    DOMAIN = re.compile(r"([\-A-Za-z0-9]+\.)+[A-Za-z]{2,6}")
    IP = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    MAILTO = re.compile(r"mailto:(\w+@\w+\.\w+)(\?subject=(.+))?")
    HTTP_LINK = re.compile(r'(http://([A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.&=\?]*)?)')
    HTTPS_LINK = re.compile(r'(https://([A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.&=\?]*)?)')
    SHORT_LINK = re.compile(r'(([A-Za-z0-9]+\.)+[A-Za-z]{2,6}(:[\d]{1,5})?([/A-Za-z0-9\.=&\?]*)?)')


def inspect_headers(headers: dict):
    has_spf = spf_pass(headers)
    has_dkim = dkim_pass(headers)
    has_dmarc = dmarc_pass(headers)
    domain_matches = from_domain_matches_received(headers)
    auth_warn = has_auth_warning(headers)
    return (has_spf, has_dkim, has_dmarc, domain_matches, auth_warn)

def spf_pass(headers: dict) -> bool:
    spf = headers.get('Received-SPF') or headers.get('Authentication-Results') or headers.get('Authentication-results')
    if spf is not None and 'pass' in spf.lower():
        return True
    return False

def dkim_pass(headers: dict) -> bool:
    if headers.get('DKIM-Signature') is not None:
        return True
    dkim = headers.get('Authentication-Results') or headers.get('Authentication-results')
    if dkim is not None and 'dkim=pass' in dkim.lower():
        return True
    return False

def dmarc_pass(headers: dict) -> bool:
    dmarc = headers.get('Authentication-Results') or headers.get('Authentication-results')
    if dmarc is not None and 'dmarc=pass' in dmarc.lower():
        return True
    return False

def has_auth_warning(headers: dict) -> bool:
    if headers.get('X-Authentication-Warning') is not None:
        return True
    return False

def from_domain_matches_received(headers: dict) -> bool:
    email_domain = get_domain(headers.get('From') or 'not found')
    server_domain = get_domain(headers.get('Received') or 'unknown')

    if len(email_domain.name) < len(server_domain.name):
        result = email_domain.name in server_domain.name
    else:
        result = server_domain.name in email_domain.name

    return ( email_domain == server_domain ) or result

def get_domain(field: str):
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
    body = body.lower()
    has_http_links = has_unsecure_links(body, domain)
    has_script = has_script_tag(body)
    forbidden_words_percentage = percentage_of_bad_words(body, wordlist)

    return (has_http_links, has_script, forbidden_words_percentage)

def percentage_of_bad_words(body, wordlist) -> float:
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
    for mail in mailto:
        links.append(mail[0])

    return links

def https_only(links: list[str]) -> bool:
    for link in links:
        if 'https://' not in link:
            return False
    return True

def has_unsecure_links(body, domain) -> bool:
    # TODO: add filter for redirect links
    if 'http://' in body:
        # if the domain is not in the received header, it's a spam
        if domain.name is not None and 'http://' + domain.name in body:
            return False
        return True
    return False

def has_script_tag(body) -> bool:
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
