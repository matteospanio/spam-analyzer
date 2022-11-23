import mailparser, socket, yaml
import dns.resolver, dns.name
from dataclasses import dataclass
from datetime import datetime

import spamdetector.analyzer.classifier as classifier
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

    def __eq__(self, __o: object) -> bool:
        result, _, _, = self.name.fullcompare(__o.name)
        if result in [1, 2, 3]:
            return True
        return False

@dataclass
class MailAnalysis:
    """A summary of the analysis of a mail"""

    file_path: str
    """The path of the file analyzed"""

    # data from headers
    headers: dict
    """It is `True` if the mail has a SPF header:
    ### SPF: Sender Policy Framework
    The SPF record is a TXT record that contains a policy that specifies which mail servers are allowed to send email from a specified domain.
    """
    """IT is `True` if the mail has a DKIM header:
    ### DKIM: DomainKeys Identified Mail
    The DKIM signature is a digital signature that is added to an email message to verify that the message has not been altered since it was signed.
    """
    """It is `True` if the mail has a DMARC header:
    ### DMARC: Domain-based Message Authentication, Reporting & Conformance
    The DMARC record is a type of DNS record that is used to help email receivers determine whether an email is legitimate or not.
    """
    """It is `True` if the mail has an Authentication-Warning header
    The Authentication-Warning header is used to indicate that the message has been modified in transit.
    """
    """It is `True` if the mail's subject contains a suspicious word or a gappy word (e.g. `H*E*L*L*O`)"""

    # attachments
    attachments: dict

    # data from body
    body: dict
    """It is `True` if the body contains a script tag or a callback function
    Email clients that support JavaScript can execute the script in the email.
    """
    """The rate of forbidden words in the body of the mail, it is a float between 0 and 1
    The formula is: `forbidden_words_count / total_bodyy_words_count`
    """

    def is_spam(self) -> bool:
        """Determine if the email is spam based on the score and the threshold set in the `config.yaml` file
        ## Spam detection
        The mail gain a score based on the presence of some headers and the content of the body.
        """
        
        with open('conf/config.yaml', 'r') as f:
            model_path = yaml.safe_load(f)['files']['classifier']
        
        model = classifier.load_model(model_path)
        return True if model.predict(self.to_list()) == 1 else False

    def get_score(self) -> int:       
        """It evaluates the mail and return a score based on the presence of some headers and the content of the body.
        The points are assigned based on the `weights` parameter.
        """
        
        # TODO: think where to pass config, we should use a dependency injection
        with open('conf/config.yaml', 'r') as f:
            weights = yaml.safe_load(f)['weights']

        score = 0

        # headers scoring
        if self.headers["has_spf"] or self.headers["domain_matches"]:
            pass
        else:
            if not self.headers["has_spf"]:
                score += weights['has_spf']
            if not self.headers["domain_matches"]:
                score += weights['domain_matches']

        if not self.headers["has_spf"] and not self.headers["domain_matches"] and not self.body["contains_script"] and not self.body["contains_form"] and not self.body["has_links"]:
            score += -0.5

        # verify send date
        # if the date has valid format
        if type(self.headers["send_date"]) is datetime:
            # if the date is in the future
            if self.headers["send_date"].timestamp() > datetime.now().timestamp():
                # then add penalty
                score += weights['invalid_date']
            if not utils.is_valid_tz(self.headers["send_date"]):
                score += weights['invalid_date']
            
            # if email is old, it often contains http links
            score += 0 if (not self.body["https_only"] and self.headers["send_date"].year < 2010) or self.body["https_only"] else weights['contains_http_links']
        else:
            # date is not in RFC 2822 format
            score += weights['invalid_date']
        
        score += -1 if self.body["https_only"] else 0
        score += weights['bad_subject'] if self.headers["has_suspect_subject"] else 0
        score += weights['uppercase_subject'] if self.headers["subject_is_uppercase"] else 0

        # those fields are not so often used, they should have a minimal impact in score
        score += -1 if self.headers["has_dkim"] else weights['has_dkim']
        score += -1 if self.headers["has_dmarc"] else weights['has_dmarc']

        score += weights['auth_warn'] if self.headers["auth_warn"] else 0

        # body scoring
        score += self.body["forbidden_words_percentage"] * weights['forbidden_words_percentage'] * 10
        score += weights['has_html_form'] if self.body["contains_form"] else 0
        score += weights['has_script'] if self.body["contains_script"] else 0
        score += weights['has_html'] if self.body["contains_html"] else 0

        # attachments scoring
        score += weights['has_attachments'] if self.attachments["has_attachments"] else 0
        score += weights['attachment_executable'] if self.attachments["attachment_is_executable"] else 0

        return score
    
    def send_date_is_later_than(self, date: datetime) -> bool:
        """It returns `True` if the send date is later than the `date` parameter"""
        return self.headers["send_date"] > date

    def trust_domain(self) -> bool:
        if self.headers["has_spf"] or self.headers["domain_matches"]:
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_path,
            "headers": self.headers,
            "body": self.body,
            "attachments": self.attachments,
            "score": self.get_score(),
        }

    def _date_is_valid(self) -> bool:
        """It checks if the date is in RFC 2822 format"""
        return type(self.headers["send_date"]) is datetime


    def to_list(self) -> list:
        lista = [self.file_path,
                 self.headers["has_spf"],
                 self.headers["has_dkim"],
                 self.headers["has_dmarc"],
                 self.headers["domain_matches"],
                 self.headers["has_suspect_subject"],
                 self.headers["subject_is_uppercase"],
                 self.headers["send_date"],
                 self._date_is_valid(),
                 self.body["contains_script"],
                 self.body["https_only"],
                 self.body["contains_mailto_links"],
                 self.body["contains_links"],
                 self.body["forbidden_words_percentage"],
                 self.body["contains_html"],
                 self.body["contains_form"],
                 self.attachments["has_attachments"],
                 self.attachments["attachment_is_executable"]]
        return lista


class MailAnalyzer:
    """Analyze a mail and return a `MailAnalysis` object, essentiaòòy it is a factory of `MailAnalysis`.
    
    The analysis is based on the presence of some headers and the content of the body.
    """
    
    def __init__(self, wordlist):
        self.wordlist = wordlist

    def analyze(self, email_path: str, add_headers: bool = False) -> MailAnalysis:
        email = mailparser.parse_from_file(email_path)

        headers = utils.inspect_headers(email.headers, self.wordlist)
        body = utils.inspect_body(email.body, self.wordlist, self.get_domain(email_path))
        attachments = utils.inspect_attachments(email.attachments)

        return MailAnalysis(
            file_path=email_path,
            headers=headers,
            body=body,
            attachments=attachments
        )

    def get_domain(self, email_path: str) -> Domain:
        email = mailparser.parse_from_file(email_path)
        received = email.headers.get('Received')
        if received is None:
            return utils.get_domain('unknown')
        return utils.get_domain(received)

    def __repr__(self):
        return f'<MailAnalyzer(wordlist={self.wordlist})>'

class Date:
 
    _raw_date: str
    year: int
    day: int
    month: int
    timezone: str
    day_of_week: str
    
    def __init__(self, date: str):
        self._raw_date = date
        self._parse()

    def __eq__(self, other):
        # TODO
        return self._raw_date == other._raw_date

    # parse the date
    def _parse(self) -> tuple[datetime, bool]:
        try:
            return datetime.strptime(self._raw_date, '%a, %d %b %Y %H:%M:%S %z'), True
        except ValueError:
            return datetime.strptime(self._raw_date, '%a, %d %b %Y %H:%M:%S %Z'), False

    def follows_RFC2822(self) -> bool:
        return self._parse()[1]        