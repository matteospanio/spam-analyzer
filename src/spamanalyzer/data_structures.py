import io
import sys
from dataclasses import dataclass
from functools import wraps
from importlib import resources
from typing import List, Optional

import mailparser
import numpy as np

from spamanalyzer import utils
from spamanalyzer.domain import Domain
from spamanalyzer.ml import SpamClassifier


def silent(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Redirect stdout to a StringIO object
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            result = func(*args, **kwargs)
        finally:
            # Reset stdout to its original value after the function call
            sys.stdout = original_stdout

        return result

    return wrapper


@dataclass
class MailAnalysis:
    """A summary of the analysis of a mail."""

    file_path: str
    """The path of the file analyzed."""

    # data from headers
    headers: dict
    """
    It is a dictionaty containing a detailed analysis of the mail's headers.
    It contains the following keys:

    | Key | Type |  Description |
    | --- | --- | --- |
    | `has_spf` | bool | flag that indicates if the mail has a SPF header |
    | `has_dkim` | bool | flag that indicates if the mail has a DKIM header |
    | `has_dmarc` | bool | flag that indicates if the mail has a DMARC header |
    | `auth_warn` | bool | flag that indicates if the mail has an Authentication-Warning header |
    | `domain_matches` | bool | flag that indicates if the domain
    of the sender matches the first domain in the `Received` headers |
    | `has_suspect_subject` | bool | flag that indicates if the mail's subject contains
    a suspicious word or a gappy word (e.g. `H*E*L*L*O`) |
    | `subject_is_uppercase` | bool | flag that indicates if the mail's subject is in uppercase |
    | `send_date` | Date | the date when the mail was sent, if the mail has no `Date` header, it is `None` |
    | `received_date` | Date | the date when the mail was received, if the mail hasn't a date
    in `Received` header, it is `None` |

    - `has_spf`, it is `True` if the mail has a SPF header (Sender Policy Framework),
      it is a standard to prevent email spoofing.
      The SPF record is a TXT record that contains a policy that specifies which mail
      servers are allowed to send email from a specified domain.
    - `has_dkim`, it is `True` if the mail has a DKIM header
      (DomainKeys Identified Mail).
      The DKIM signature is a digital signature that is added to an email message to
      verify that the message has not been altered since it was signed.
    - `has_dmarc`, it is `True` if the mail has a DMARC header (Domain-based Message
      Authentication, Reporting & Conformance).
      The DMARC record is a type of DNS record that is used to help email receivers
      determine whether an email is legitimate or not.
    - `auth_warn`, it is `True` if the mail has an Authentication-Warning header
      The Authentication-Warning header is used to indicate that the message has been
      modified in transit.
    - `domain_matches`, it is `True` if the domain of the sender matches the first
      domain in the `Received` headers
    - `has_suspect_subject`, it is `True` if the mail's subject contains a suspicious
      word or a gappy word (e.g. `H*E*L*L*O`)
    - `subject_is_uppercase`, it is `True` if the mail's subject is in uppercase
    - `send_date`, it is the date when the mail was sent in a `Date` object,
      if the mail has no `Date` header, it is `None`
    - `received_date`, it is the date when the mail was received in a `Date` object,
      if the mail hasn't a date in `Received` header, it is `None`
    """

    # data from body
    body: dict
    """
    It is a dictionaty containing a detailed analysis of the mail's body.
    It contains the following keys:

    | Key | Type |  Description |
    | --- | --- | --- |
    | `contains_html` | bool | flag that indicates if the body contains an html tag |
    | `contains_script` | bool | flag that indicates if the body contains a script tag or a callback function |
    | `forbidden_words_percentage` | float | the rate of forbidden words in the body of the mail, it is a float between 0 and 1 |
    | `has_links` | bool | flag that indicates if the body contains an url |
    | `has_mailto` | bool | flag that indicates if the body contains a mailto link |
    | `https_only` | bool | flag that indicates if the body contains only https links |
    | `contains_form` | bool | flag that indicates if the body contains a form tag |
    | `has_images` | bool | flag that indicates if the body contains an image |
    | `is_uppercase` | bool | flag that indicates if the body is in uppercase more than $60$% of its length |
    | `text_polarity` | float | the polarity of the body, it is a float between -1 and 1 |
    | `text_subjectivity` | float | the subjectivity of the body, it is a float between 0 and 1 |
    """

    # attachments
    attachments: dict
    """
    It is a dictionary containing a detailed analysis of the mail's attachments.
    It contains the following keys:

    | Key | Type |  Description |
    | --- | --- | --- |
    | `has_attachments` | bool | flag that indicates if the mail has attachments |
    | `attachment_is_executable` | bool | flag that indicates if the mail has an attachment in executable format |
    """

    def to_dict(self) -> dict:
        return {
            "headers": self.headers,
            "body": self.body,
            "attachments": self.attachments,
        }

    def to_list(self) -> List:
        return [
            self.headers["has_spf"],
            self.headers["has_dkim"],
            self.headers["has_dmarc"],
            self.headers["domain_matches"],
            self.headers["auth_warn"],
            self.headers["has_suspect_subject"],
            self.headers["subject_is_uppercase"],
            self.headers["send_date"].is_RFC2822_formatted()
            if self.headers["send_date"] is not None else False,
            self.headers["send_date"].is_tz_valid()
            if self.headers["send_date"] is not None else False,
            self.headers["received_date"] is not None,
            self.body["is_uppercase"],
            self.body["contains_script"],
            self.body["has_images"],
            self.body["https_only"],
            self.body["has_mailto"],
            self.body["has_links"],
            self.body["forbidden_words_percentage"],
            self.body["contains_html"],
            self.body["contains_form"],
            self.body["text_polarity"],
            self.body["text_subjectivity"],
            self.attachments["has_attachments"],
            self.attachments["attachment_is_executable"],
        ]


class SpamAnalyzer:
    """Analyze a mail and return a `MailAnalysis` object, essentially it is a
    factory of `MailAnalysis`.

    The `MailAnalyzer` object provides two methods to analyze a mail:

    - `analyze` to analyze a mail from a file, it returns a `MailAnalysis`
      object containing a description of the headers, body and attachments of the mail
    - `get_domain` to get the domain of the mail from the headers,
      it returns a `Domain` object

    The core of the analysis is the `analyze` method, it uses the `MailParser` class
    (from `mailparser` library) to parse the mail.
    The analysis is based on separated checks for the headers, body and attachments and
    each check is implemented in a separated function: this make the analysis modular
    and easy to extend in future versions.

    """

    __model: str
    __wordlist: List[str]

    def __init__(self, wordlist: List[str], model: Optional[str] = None):
        self.__wordlist = wordlist

        if model is None:
            model = str(resources.files("spamanalyzer.ml").joinpath("classifier.pkl"))

        self.__model = model  # type: ignore

    @staticmethod
    @silent
    def parse(email_path: str) -> mailparser.MailParser:
        return mailparser.parse_from_file(email_path)

    async def analyze(self, email_path: str) -> MailAnalysis:
        email = SpamAnalyzer.parse(email_path)

        headers = await utils.inspect_headers(email, self.__wordlist)
        body = utils.inspect_body(email.body, self.__wordlist,
                                  (await self.get_domain(email_path)))
        attachments = utils.inspect_attachments(email.attachments)

        return MailAnalysis(file_path=email_path,
                            headers=headers,
                            body=body,
                            attachments=attachments)

    async def get_domain(self, email_path: str) -> Domain:
        email = SpamAnalyzer.parse(email_path)
        received = email.headers.get("Received")
        return await utils.get_domain("unknown" if received is None else received)

    def is_spam(self, email: MailAnalysis) -> bool:
        """Determine if the email is spam based on the analysis of the mail."""

        model = SpamClassifier(self.__model)
        array = np.array(email.to_list())
        return True if model.predict(array.reshape(1, -1)) == 1 else False

    def classify_multiple_input(self, mails: List["MailAnalysis"]) -> List[bool]:
        """Classify a list of mails.

        Args:
            mails (list[MailAnalysis]): a list of mails to be classified

        Returns:
            list: a list of boolean values, `True` if the mail is spam, `False`
            otherwise

        """

        model = SpamClassifier(self.__model)

        # rearrange input
        adapted_mails = [np.array(mail.to_list()) for mail in mails]
        predictions = model.predict(adapted_mails)
        return [prediction == 1 for prediction in predictions]

    def __repr__(self):
        return f"<MailAnalyzer(wordlist={self.__wordlist})>"
