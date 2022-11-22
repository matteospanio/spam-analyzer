import mailparser, socket, yaml
import dns.resolver, dns.name
from dataclasses import dataclass
from datetime import datetime

import spamdetector.analyzer.utils as utils


@dataclass
class Domain:
    """
    A Domain is a class representing an internet domain, here you can get information about the target domain
    """

    name: dns.name.Name

    def __init__(self, name: str) -> None:
        """The constructor resolves any domain alias to the real domain name:
        in fact common domain names are aliases for more complex server names that would be difficult to remember for common users,
        since there is not a direct method in the `socket` module to resolve domain aliases, we use the `gethostbyname` chained with the `gethostbyaddr` methods
        this way makes the instatiation of the class slower, but it is the only way to get the real domain name.
        """
        # TODO: add a cache for the domain names or find a better way to resolve domain aliases
        # try:
        #     ip = socket.gethostbyname(name)
        #     self.name = socket.gethostbyaddr(ip)[0]
        # except Exception:
        #     # if the name is not a valid domain name, we just use it
        #     self.name = name
        self.name = dns.name.from_text(name)

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
        It translate the ip address to its domain name via the `socket.gethostbyaddr` method

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
        return dns.resolver.resolve(self.name, 'A')[0].to_text()

    def is_trustable(self):
        pass

    def __eq__(self, __o: object) -> bool:
        result, _, _, = self.name.fullcompare(__o.name)
        if result in [1, 2, 3]:
            return True
        return False

@dataclass
class MailAnalysis:
    """A summary of the analysis of a mail"""
    spamassassin: str

    file_path: str
    """The path of the file analyzed"""

    # data from headers
    has_spf: bool
    """It is `True` if the mail has a SPF header:
    ### SPF: Sender Policy Framework
    The SPF record is a TXT record that contains a policy that specifies which mail servers are allowed to send email from a specified domain.
    """
    has_dkim: bool
    """IT is `True` if the mail has a DKIM header:
    ### DKIM: DomainKeys Identified Mail
    The DKIM signature is a digital signature that is added to an email message to verify that the message has not been altered since it was signed.
    """
    has_dmarc: bool
    """It is `True` if the mail has a DMARC header:
    ### DMARC: Domain-based Message Authentication, Reporting & Conformance
    The DMARC record is a type of DNS record that is used to help email receivers determine whether an email is legitimate or not.
    """
    domain_matches: bool
    auth_warn: bool
    """It is `True` if the mail has an Authentication-Warning header
    The Authentication-Warning header is used to indicate that the message has been modified in transit.
    """
    has_suspect_subject: bool
    """It is `True` if the mail's subject contains a suspicious word or a gappy word (e.g. `H*E*L*L*O`)"""
    subject_is_uppercase: bool

    send_date: datetime | None

    # attachments
    has_attachments: bool

    is_attachment_executable: bool

    # data from body
    contains_script: bool
    """It is `True` if the body contains a script tag or a callback function
    Email clients that support JavaScript can execute the script in the email.
    """
    contains_links: bool
    contains_mailto_links: bool
    https_only: bool
    forbidden_words_percentage: float
    """The rate of forbidden words in the body of the mail, it is a float between 0 and 1
    The formula is: `forbidden_words_count / total_bodyy_words_count`
    """
    contains_form: bool
    contains_html: bool

    def is_spam(self) -> bool:
        """Determine if the email is spam based on the score and the threshold set in the `config.yaml` file
        ## Spam detection
        The mail gain a score based on the presence of some headers and the content of the body.
        """
        if self.contains_script or self.auth_warn:
            return 'Spam'
        if (not self.has_spf and not self.domain_matches):
            return 'Spam'
        if (self.has_spf or self.domain_matches) and not self.https_only and self.forbidden_words_percentage > 0.05:
            return 'Warning'
        else:
            return 'Ham'

    def get_score(self) -> int:       
        """It evaluates the mail and return a score based on the presence of some headers and the content of the body.
        The points are assigned based on the `weights` parameter.
        """
        
        # TODO: think where to pass config, we should use a dependency injection
        with open('conf/config.yaml', 'r') as f:
            weights = yaml.safe_load(f)['weights']

        score = 0

        # headers scoring
        if self.has_spf or self.domain_matches:
            pass
        else:
            if not self.has_spf:
                score += weights['has_spf']
            if not self.domain_matches:
                score += weights['domain_matches']

        if not self.has_spf and not self.domain_matches and not self.contains_script and not self.contains_form and not self.contains_links:
            score += -0.5

        # verify send date
        # if the date has valid format
        if type(self.send_date) is datetime:
            # if the date is in the future
            if self.send_date.timestamp() > datetime.now().timestamp():
                # then add penalty
                score += weights['invalid_date']
            if not utils.is_valid_tz(self.send_date):
                score += weights['invalid_date']
            
            # if email is old, it often contains http links
            score += 0 if (not self.https_only and self.send_date.year < 2010) or self.https_only else weights['contains_http_links']
        else:
            # date is not in RFC 2822 format
            score += weights['invalid_date']
        
        score += -1 if self.https_only else 0
        score += weights['bad_subject'] if self.has_suspect_subject else 0
        score += weights['uppercase_subject'] if self.subject_is_uppercase else 0

        # those fields are not so often used, they should have a minimal impact in score
        score += -1 if self.has_dkim else weights['has_dkim']
        score += -1 if self.has_dmarc else weights['has_dmarc']

        score += weights['auth_warn'] if self.auth_warn else 0

        # body scoring
        score += self.forbidden_words_percentage * weights['forbidden_words_percentage'] * 10
        score += weights['has_html_form'] if self.contains_form else 0
        score += weights['has_script'] if self.contains_script else 0
        score += weights['has_html'] if self.contains_html else 0

        # attachments scoring
        score += weights['has_attachments'] if self.has_attachments else 0
        score += weights['attachment_executable'] if self.is_attachment_executable else 0

        return score

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_path,
            "headers": {
                "has_spf": self.has_spf,
                "has_dkim": self.has_dkim,
                "has_dmarc": self.has_dmarc,
                "domain_matches": self.domain_matches,
                "auth_warn": self.auth_warn,
                "has_suspect_subject": self.has_suspect_subject,
                "subject_is_uppercase": self.subject_is_uppercase,
                "send_date": self.send_date
            },
            "body": {
                "contains_script": self.contains_script,
                "https_only": self.https_only,
                "contains_mailto_links": self.contains_mailto_links,
                "contains_links": self.contains_links,
                "forbidden_words_percentage": self.forbidden_words_percentage,
                "contains_html": self.contains_html,
                "contains_form": self.contains_form,
            },
            "attachments": {
                "has_attachments": self.has_attachments,
                "is_attachment_executable": self.is_attachment_executable
            },
            "is_spam": self.is_spam(),
            "score": self.get_score(),
            "spamassassin": self.spamassassin
        }

    def _date_is_valid(self) -> bool:
        """It checks if the date is in RFC 2822 format"""
        return type(self.send_date) is datetime


    def to_list(self) -> list:
        lista = [self.file_path,
                 self.has_spf,
                 self.has_dkim,
                 self.has_dmarc,
                 self.domain_matches,
                 self.has_suspect_subject,
                 self.subject_is_uppercase,
                 self.send_date,
                 self._date_is_valid(),
                 self.contains_script,
                 self.https_only,
                 self.contains_mailto_links,
                 self.contains_links,
                 self.forbidden_words_percentage,
                 self.contains_html,
                 self.contains_form,
                 self.has_attachments,
                 self.is_attachment_executable]
        return lista


class MailAnalyzer:
    """Analyze a mail and return a `MailAnalysis` object, essentiaòòy it is a factory of `MailAnalysis`.
    
    The analysis is based on the presence of some headers and the content of the body.
    """
    
    def __init__(self, wordlist):
        self.wordlist = wordlist

    def analyze(self, email_path: str, add_headers: bool = False) -> MailAnalysis:
        email = mailparser.parse_from_file(email_path)

        has_spf, has_dkim, has_dmarc, domain_matches, auth_warn, has_suspect_subject, subject_is_uppercase , send_date = utils.inspect_headers(email.headers, self.wordlist)
        contains_links, contains_mailto, https_only, contains_script, forbidden_words_percentage, has_form, contains_html = utils.inspect_body(email.body, self.wordlist, self.get_domain(email_path))
        has_attachments, is_executable = utils.inspect_attachments(email.attachments)

        return MailAnalysis(
            file_path=email_path,
            has_spf=has_spf,
            has_dkim=has_dkim,
            has_dmarc=has_dmarc,
            domain_matches=domain_matches,
            auth_warn=auth_warn,
            contains_links=contains_links,
            contains_mailto_links=contains_mailto,
            https_only=https_only,
            contains_script=contains_script,
            forbidden_words_percentage=forbidden_words_percentage,
            has_attachments=has_attachments,
            is_attachment_executable=is_executable,
            has_suspect_subject=has_suspect_subject,
            subject_is_uppercase=subject_is_uppercase,
            contains_form=has_form,
            send_date=send_date,
            contains_html=contains_html,
            spamassassin=utils.inspect_spamassassin(email.headers)
        )

    def get_domain(self, email_path: str) -> Domain:
        email = mailparser.parse_from_file(email_path)
        received = email.headers.get('Received')
        if received is None:
            return utils.get_domain('unknown')
        return utils.get_domain(received)

    def __repr__(self):
        return f'<MailAnalyzer(wordlist={self.wordlist})>'
