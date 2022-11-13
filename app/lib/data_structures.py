import mailparser, socket
from mailparser import MailParser
from dataclasses import dataclass

import app.lib.utils as utils


@dataclass
class Domain:
    """
    A Domain is a class representing an internet domain, here you can get information about the target domain
    """

    name: str

    @staticmethod
    def from_string(domain_str: str):
        """
        Instantiate a Domain object from string, it is a wrapper of the `self.__init__` method

        Args:
            domain_str (str): a string containing a domain to be parsed

        Returns:
            Domain: the domain obtained from the string
        """
        return Domain(domain_str)

    @staticmethod
    def from_ip(ip_addr: str):
        try:
            domain_name = socket.gethostbyaddr(ip_addr)[0]
            return Domain(domain_name)
        except Exception:
            return Domain('unknown')

    def get_ip_address(self) -> str:
        """Translate the domain name to its ip address"""
        return socket.gethostbyname(self.name)

    def is_trustable(self):
        pass


@dataclass
class MailAnalysis:

    file_path: str

    # data from headers
    has_spf: bool
    has_dkim: bool
    has_dmarc: bool
    domain_matches: bool
    auth_warn: bool

    # data from body
    contains_script: bool
    contains_http_links: bool
    contains_forbidden_words: bool

    def is_spam(self) -> str:
        if self.contains_script or self.auth_warn:
            return 'Spam'
        if (not self.has_spf and not self.domain_matches):
            return 'Spam'
        if (self.has_spf or self.domain_matches) and self.contains_http_links and self.contains_forbidden_words:
            return 'Warning'
        else:
            return 'Trust' 


class MailAnalyzer:
    def __init__(self, wordlist, ignore_headers=False, ignore_body=False):
        self.wordlist = wordlist
        self.ignore_headers = ignore_headers
        self.ignore_body = ignore_body

    def analyze(self, email_path: str) -> MailAnalysis:
        email = mailparser.parse_from_file(email_path)
        domain = self.get_domain(email)

        has_spf, has_dkim, has_dmarc, domain_matches, auth_warn = utils.inspect_headers(email.headers)
        contains_forbidden_words, contains_http_links, contains_script = utils.inspect_body(email.body, self.wordlist, domain)

        return MailAnalysis(
            file_path=email_path,
            has_spf=has_spf,
            has_dkim=has_dkim,
            has_dmarc=has_dmarc,
            domain_matches=domain_matches,
            auth_warn=auth_warn,
            contains_forbidden_words=contains_forbidden_words,
            contains_http_links=contains_http_links,
            contains_script=contains_script
        )

    def get_domain(self, email: MailParser) -> Domain:
        received = email.headers.get('Received')
        if received is None:
            return utils.get_domain('unknown')
        return utils.get_domain(received)

    def __repr__(self):
        return f'<MailAnalyzer(wordlist={self.wordlist}, ignore_headers={self.ignore_headers}, ignore_body={self.ignore_body})>'
