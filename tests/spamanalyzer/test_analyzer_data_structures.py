import os
import pytest
from spamanalyzer.data_structures import (
    MailAnalysis,
    MailAnalyzer,
)
from spamanalyzer.domain import Domain
from app.files import handle_configuration_files

SAMPLES_FOLDER = "tests/samples"

trustable_mail = os.path.join(
    SAMPLES_FOLDER,
    "97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email",
)
spam = os.path.join(
    SAMPLES_FOLDER,
    "00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email",
)

with open("conf/word_blacklist.txt", "r", encoding="utf-8") as f:
    wordlist = f.read().splitlines()

_, _, _ = handle_configuration_files()


class TestMailAnalyzer:

    def test_get_domain(self):
        analyzer = MailAnalyzer(wordlist)
        assert analyzer.get_domain(trustable_mail) == Domain(
            "github-lowworker-5fb2734.va3-iad.github.net")


class TestMailAnalysis:
    analyzer = MailAnalyzer(wordlist)

    mail_ok_an = analyzer.analyze(trustable_mail)
    mail_spam = analyzer.analyze(spam)

    def test_mail_analysis_type(self):
        assert isinstance(self.mail_ok_an, MailAnalysis)

    def test_mail_analysis_file_path(self):
        assert self.mail_ok_an.file_path == trustable_mail

    def test_mail_analysis_is_spam(self):
        assert self.mail_ok_an.is_spam() is False

    def test_multiple_analysis(self):
        assert MailAnalysis.classify_multiple_input([self.mail_ok_an,
                                                     self.mail_spam]) == [False, True]

    def test_to_dict(self):
        dict_mail = self.mail_ok_an.to_dict()
        assert isinstance(dict_mail, dict)
        assert dict_mail["file_name"] == trustable_mail
        assert dict_mail["is_spam"] is False
        with pytest.raises(KeyError):
            assert dict_mail["not_existing_key"] is None
