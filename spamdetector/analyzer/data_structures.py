import mailparser, socket
from mailparser import MailParser
from dataclasses import dataclass

import spamdetector.analyzer.utils as utils


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
        """Create a Domain object from an ip address.
        It translate the ip address to its domain name with the `socket.gethostbyaddr` method

        Args:
            ip_addr (str): the targetted ip address

        Returns:
            Domain: the domain obtained from the ip address
        """
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
    """A summary of the analysis of a mail"""

    file_path: str
    """The path of the file analyzed"""

    # data from headers
    has_spf: bool
    """It is `True` if the mail has a SPF header:
    ## SPF: Sender Policy Framework
    The SPF record is a TXT record that contains a policy that specifies which mail servers are allowed to send email from a specified domain.
    """
    has_dkim: bool
    """IT is `True` if the mail has a DKIM header:
    ## DKIM: DomainKeys Identified Mail
    The DKIM signature is a digital signature that is added to an email message to verify that the message has not been altered since it was signed.
    """
    has_dmarc: bool
    """It is `True` if the mail has a DMARC header:
    ## DMARC: Domain-based Message Authentication, Reporting & Conformance
    The DMARC record is a type of DNS record that is used to help email receivers determine whether an email is legitimate or not.
    """
    domain_matches: bool
    auth_warn: bool
    """It is `True` if the mail has an Authentication-Warning header
    The Authentication-Warning header is used to indicate that the message has been modified in transit.
    """
    has_suspect_subject: bool

    # attachments
    has_attachments: bool
    is_attachment_executable: bool

    # data from body
    contains_script: bool
    """It is `True` if the body contains a script tag or a callback function
    Email clients that support JavaScript can execute the script in the email.
    """
    contains_http_links: bool
    forbidden_words_percentage: float
    """The rate of forbidden words in the body of the mail, it is a float between 0 and 1
    The formula is: `forbidden_words_count / total_bodyy_words_count`
    """
    contains_form: bool

    def is_spam(self) -> str:
        """Determine if the email is spam based on the score and the threshold set in the `config.yaml` file
        ## Spam detection
        The mail gain a score based on the presence of some headers and the content of the body.
        """
        if self.contains_script or self.auth_warn:
            return 'Spam'
        if (not self.has_spf and not self.domain_matches):
            return 'Spam'
        if (self.has_spf or self.domain_matches) and self.contains_http_links and self.forbidden_words_percentage > 0.05:
            return 'Warning'
        else:
            return 'Trust'

    def get_score(self, weights) -> int:
        """It evaluates the mail and return a score based on the presence of some headers and the content of the body.
        The points are assigned based on the `weights` parameter.
        """
        # headers scoring
        has_spf = 0 if self.has_spf else weights['has_spf']
        has_dkim = 0 if self.has_dkim else weights['has_dkim']
        has_dmarc = 0 if self.has_dmarc else weights['has_dmarc']
        domain_matches = 0 if self.domain_matches else weights['domain_matches']

        # body scoring
        forbidden_words_percentage = self.forbidden_words_percentage * weights['forbidden_words_percentage'] * 10

        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_path,
            "headers": {
                "has_spf": self.has_spf,
                "has_dkim": self.has_dkim,
                "has_dmarc": self.has_dmarc,
                "domain_matches": self.domain_matches,
                "auth_warn": self.auth_warn,
                "has_suspect_subject": self.has_suspect_subject
            },
            "body": {
                "contains_script": self.contains_script,
                "contains_http_links": self.contains_http_links,
                "forbidden_words_percentage": self.forbidden_words_percentage,
                "contains_form": self.contains_form
            },
            "attachments": {
                "has_attachments": self.has_attachments,
                "is_attachment_executable": self.is_attachment_executable
            },
            "is_spam": self.is_spam()
        }


class MailAnalyzer:
    def __init__(self, wordlist):
        self.wordlist = wordlist

    def analyze(self, email_path: str, add_headers) -> MailAnalysis:
        email = mailparser.parse_from_file(email_path)

        has_spf, has_dkim, has_dmarc, domain_matches, auth_warn = utils.inspect_headers(email.headers)
        contains_http_links, contains_script, forbidden_words_percentage = utils.inspect_body(email.body, self.wordlist, self.get_domain(email))
        has_attachments, is_executable = utils.inspect_attachments(email.attachments)

        return MailAnalysis(
            file_path=email_path,
            has_spf=has_spf,
            has_dkim=has_dkim,
            has_dmarc=has_dmarc,
            domain_matches=domain_matches,
            auth_warn=auth_warn,
            contains_http_links=contains_http_links,
            contains_script=contains_script,
            forbidden_words_percentage=forbidden_words_percentage,
            has_attachments=has_attachments,
            is_attachment_executable=is_executable,
            has_suspect_subject=True,
            contains_form=True
        )

    def get_domain(self, email: MailParser) -> Domain:
        received = email.headers.get('Received')
        if received is None:
            return utils.get_domain('unknown')
        return utils.get_domain(received)

    def __repr__(self):
        return f'<MailAnalyzer(wordlist={self.wordlist})>'
