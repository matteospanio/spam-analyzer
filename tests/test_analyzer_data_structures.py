from spamanalyzer.analyzer.data_structures import Domain, MailAnalysis, MailAnalyzer, Date
from spamanalyzer.files import handle_configuration_files
import socket, pytest
from dateutil.parser import parse

trustable_mail = 'tests/samples/97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email'
spam = 'tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email'

with open('conf/word_blacklist.txt', 'r') as f:
    wordlist = f.read().splitlines()

_, _, _ = handle_configuration_files()


class TestDomainMethods:

    domain = Domain('localhost')
    ip_addr = socket.gethostbyname('localhost')

    def test_from_string(self):
        assert self.domain == Domain.from_string('localhost')

    def test_get_ip_address(self):
        assert self.domain.get_ip_address() == self.ip_addr


class TestMailAnalyzer:

    def test_get_domain(self):
        analyzer = MailAnalyzer(wordlist)
        assert analyzer.get_domain(trustable_mail) == Domain(
            'github-lowworker-5fb2734.va3-iad.github.net')


class TestMailAnalysis:

    analyzer = MailAnalyzer(wordlist)

    mail_ok_an = analyzer.analyze(trustable_mail)

    def test_mail_analysis_type(self):
        assert type(self.mail_ok_an) == MailAnalysis

    def test_mail_analysis_file_path(self):
        assert self.mail_ok_an.file_path == trustable_mail

    def test_mail_analysis_is_spam(self):
        assert self.mail_ok_an.is_spam() == False


class TestDate:

    RFC_date = 'Wed, 17 Feb 2021 10:00:00 +0100'
    invalid_date = 'Wed, 17 Feb 2021 10:00:00'
    date_plus_0 = 'Wed, 17 Feb 2021 10:00:00 +0000'
    invalid_utc = 'Wed, 17 Feb 2021 10:00:00 +1900'
    empty_date = ''

    def test_successful_date_creation(self):
        date1 = Date(self.RFC_date)
        date2 = Date(self.invalid_date)

        assert date1.date == parse(self.RFC_date)
        assert date2.date == parse(self.invalid_date)

    def test_RFC_2822_format(self):
        date1 = Date(self.RFC_date)
        date2 = Date(self.invalid_date)
        date3 = Date(self.invalid_utc)

        assert date1.is_RFC2822_formatted() == True
        assert date2.is_RFC2822_formatted() == False
        assert date3.is_RFC2822_formatted() == True

    def test_is_tz_valid(self):
        date1 = Date(self.RFC_date)
        date2 = Date(self.invalid_date)
        date3 = Date(self.invalid_utc)

        assert date1.is_tz_valid() == True
        assert date2.is_tz_valid() == False
        assert date3.is_tz_valid() == False

    def test_empty_date_creation(self):
        with pytest.raises(ValueError):
            Date(self.empty_date)
