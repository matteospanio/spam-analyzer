import mailparser, socket, yaml
import dns.resolver, dns.name
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from os import path
from dateutil.parser import parse, ParserError

import spamanalyzer.analyzer.classifier as classifier
import spamanalyzer.analyzer.utils as utils


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
        """Translate the domain name to its ip address querying the DNS server"""
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
    """
    It is a dictionaty containing a detailed analysis of the mail's headers. It contains the following keys:
    
    - `has_spf`, it is `True` if the mail has a SPF header (Sender Policy Framework), it is a standard to prevent email spoofing.
      The SPF record is a TXT record that contains a policy that specifies which mail servers are allowed to send email from a specified domain.
    - `has_dkim`, it is `True` if the mail has a DKIM header (DomainKeys Identified Mail).
      The DKIM signature is a digital signature that is added to an email message to verify that the message has not been altered since it was signed.
    - `has_dmarc`, it is `True` if the mail has a DMARC header (Domain-based Message Authentication, Reporting & Conformance).
      The DMARC record is a type of DNS record that is used to help email receivers determine whether an email is legitimate or not.
    - `auth_warn`, it is `True` if the mail has an Authentication-Warning header
      The Authentication-Warning header is used to indicate that the message has been modified in transit.
    - `domain_matches`, it is `True` if the domain of the sender matches the first domain in the `Received` headers
    - `has_suspect_subject`, it is `True` if the mail's subject contains a suspicious word or a gappy word (e.g. `H*E*L*L*O`)
    - `subject_is_uppercase`, it is `True` if the mail's subject is in uppercase
    - `send_date`, it is the date when the mail was sent in a `Date` object, if the mail has no `Date` header, it is `None`
    - `received_date`, it is the date when the mail was received in a `Date` object, if the mail hasn't a date in `Received` header, it is `None`
    """

    # data from body
    body: dict
    """
    It is a dictionaty containing a detailed analysis of the mail's body. It contains the following keys:
    
    - `contains_html`, it is `True` if the body contains an html tag.
    - `contains_script`, it is `True` if the body contains a script tag or a callback function. It is dangerous because Email clients that support JavaScript can execute the script in the email.
    - `forbidden_words_percentage`, the rate of forbidden words in the body of the mail, it is a float between 0 and 1.
    - `has_links`, it is `True` if the body contains an url.
    - `has_mailto`, it is `True` if the body contains a mailto link.
    - `https_only`, it is `True` if the body contains only https links.
    - `contains_form`, it is `True` if the body contains a form tag.
    - `has_images`, it is `True` if the body contains an image.
    - `is_uppercase`, it is `True` if the body is in uppercase more than $60\%$ of its length.
    - `text_polarity`, it is the polarity of the body, it is a float between -1 and 1.
    - `text_subjectivity`, it is the subjectivity of the body, it is a float between 0 and 1.
    """

    # attachments
    attachments: dict
    """
    It is a dictionary containing a detailed analysis of the mail's attachments. It contains the following keys:
    - `has_attachments`, it is `True` if the mail has attachments
    - `attachment_is_executable`, it is `True` if the mail has an attachment in executable format
    """

    @staticmethod
    def classify_multiple_input(mails: list) -> list:
        """Classify a list of mails

        Args:
            mails (list[MailAnalysis]): a list of mails to be classified

        Returns:
            list: a list of boolean values, `True` if the mail is spam, `False` otherwise
        """

        with open('conf/config.yaml', 'r') as f:
            model_path = yaml.safe_load(f)['files']['classifier']

        ml = classifier.SpamClassifier(path.expandvars(model_path))

        # rearrange input
        adapted_mails = [np.array(mail.to_list()) for mail in mails]
        predictions = ml.predict(adapted_mails)
        return [True if prediction == 1 else False for prediction in predictions]

    def is_spam(self) -> bool:
        """Determine if the email is spam based on the analysis of the mail"""

        with open('conf/config.yaml', 'r') as f:
            model_path = yaml.safe_load(f)['files']['classifier']

        ml = classifier.SpamClassifier(path.expandvars(model_path))
        array = np.array(self.to_list())
        return True if ml.predict(array.reshape(1, -1)) == 1 else False

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_path,
            "headers": self.headers,
            "body": self.body,
            "attachments": self.attachments,
            "is_spam": self.is_spam()
        }

    def to_list(self) -> list:
        return [  #self.file_path,
            self.headers["has_spf"], self.headers["has_dkim"],
            self.headers["has_dmarc"], self.headers["domain_matches"],
            self.headers["auth_warn"], self.headers["has_suspect_subject"],
            self.headers["subject_is_uppercase"],
            self.headers["send_date"].is_RFC2822_formatted()
            if self.headers["send_date"] is not None else False,
            self.headers["send_date"].is_tz_valid()
            if self.headers["send_date"] is not None else False,
            self.headers["received_date"] is not None, self.body["is_uppercase"],
            self.body["contains_script"], self.body["has_images"],
            self.body["https_only"], self.body["has_mailto"], self.body["has_links"],
            self.body["forbidden_words_percentage"], self.body["contains_html"],
            self.body["contains_form"], self.body["text_polarity"],
            self.body["text_subjectivity"], self.attachments["has_attachments"],
            self.attachments["attachment_is_executable"]
        ]


class MailAnalyzer:
    """Analyze a mail and return a `MailAnalysis` object, essentially it is a factory of `MailAnalysis`.
    
    The `MailAnalyzer` object provides two methods to analyze a mail:
    - `analyze` to analyze a mail from a file, it returns a `MailAnalysis` object containing a description of the headers, body and attachments of the mail
    - `get_domain` to get the domain of the mail from the headers, it returns a `Domain` object
    
    The core of the analysis is the `analyze` method, it uses the `MailParser` class (from `mailparser` library) to parse the mail.
    The analysis is based on separated checks for the headers, body and attachments and each check is implemented in
    a separated function: this make the analysis modular and easy to extend in future versions.
    """

    def __init__(self, wordlist):
        self.wordlist = wordlist

    def analyze(self, email_path: str) -> MailAnalysis:
        email = mailparser.parse_from_file(email_path)

        headers = utils.inspect_headers(email, self.wordlist)
        body = utils.inspect_body(email.body, self.wordlist,
                                  self.get_domain(email_path))
        attachments = utils.inspect_attachments(email.attachments)

        return MailAnalysis(file_path=email_path,
                            headers=headers,
                            body=body,
                            attachments=attachments)

    def get_domain(self, email_path: str) -> Domain:
        email = mailparser.parse_from_file(email_path)
        received = email.headers.get('Received')
        if received is None:
            return utils.get_domain('unknown')
        return utils.get_domain(received)

    def __repr__(self):
        return f'<MailAnalyzer(wordlist={self.wordlist})>'


class Date:
    """A date object, it is used to store the date of the email and to perform some checks on it.
    
    The focus of the checks is to determine if the date is valid and if it is in the correct format.
    The date is valid if it is in the RFC2822 format and if the timezone is valid:
    - [RFC2822](https://tools.ietf.org/html/rfc2822#section-3.3): specifies the format of the date in the headers of the mail in the form `Day, DD Mon YYYY HH:MM:SS TZ`. Of course it is not the only format used in the headers, but it is the most common, so it is the one we use to check if the date is valid.
    - [TZ](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones): specifies the timezone of the date. We included this check since often malicious emails can have a weird behavior, it is not uncommon to see a not existing timezone in the headers of the mail (valid timezones are from -12 to +14).
    """

    _raw_date: str
    date: datetime

    def __init__(self, date: str):
        if date is None or date == '':
            raise ValueError('Date cannot be empty or None')
        self._raw_date = date
        self.date = self._parse()[0]

    def __eq__(self, other) -> bool:
        if isinstance(other, Date):
            return self.date.timestamp() == other.date.timestamp()
        if isinstance(other, datetime):
            return self.date.timestamp() == other.timestamp()
        return False

    def to_dict(self) -> dict:
        return {
            "is_RFC_2822": self.is_RFC2822_formatted(),
            "is_tz_valid": self.is_tz_valid(),
            "date": self.date.isoformat(),
            "posix": self.date.timestamp(),
            "year": self.date.year,
            "month": self.date.month,
            "day": self.date.day,
            "hour": self.date.hour,
            "minute": self.date.minute,
            "second": self.date.second,
        }

    # parse the date
    def _parse(self) -> tuple[datetime, bool]:
        try:
            return datetime.strptime(self._raw_date, '%a, %d %b %Y %H:%M:%S %z'), True
        except ValueError:
            try:
                return parse(self._raw_date), False
            except ParserError:
                split_date = self._raw_date.split(' ')
                reduced_date = " ".join(split_date[0:5])
                return parse(reduced_date), False

    def is_RFC2822_formatted(self) -> bool:
        """Check if the date is in the [RFC2822](https://tools.ietf.org/html/rfc2822#section-3.3) format."""
        return self._parse()[1]

    def is_tz_valid(self) -> bool:
        """The timezone is valid if it is in the range [-12, 14]"""

        try:
            if -12 <= self._get_tz_offset() <= 14:
                return True
            else:
                return False
        except Exception:
            return False

    def _get_tz_offset(self) -> int:
        return int(str(self.date.tzinfo).replace('UTC', '').split(':')[0])

    def __repr__(self) -> str:
        return f'{self.date.isoformat()}'
