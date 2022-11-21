from spamdetector.analyzer.data_structures import Domain, MailAnalysis, MailAnalyzer
import socket

trustable_mail = 'tests/samples/97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email'
spam = 'tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email'

with open('conf/word_blacklist.txt', 'r') as f:
    wordlist = f.read().splitlines()


class TestDomainMethods:

    domain = Domain('google.com')
    ip_addr = socket.gethostbyname('google.com')

    def test_from_string(self):
        assert self.domain == Domain.from_string('google.com')

    def test_from_ip(self):
        assert self.domain == Domain.from_ip(self.ip_addr)

    def test_get_ip_address(self):
        assert self.domain.get_ip_address() == self.ip_addr


class TestMailAnalyzer:

    def test_get_domain(self):
        analyzer = MailAnalyzer(wordlist)
        assert analyzer.get_domain(trustable_mail) == Domain('github-lowworker-5fb2734.va3-iad.github.net')


class TestMailAnalysis:

    analyzer = MailAnalyzer(wordlist)

    mail_ok_an = analyzer.analyze(trustable_mail)

    def test_mail_analysis_type(self):
        assert type(self.mail_ok_an) == MailAnalysis

    def test_mail_analysis_file_path(self):
        assert self.mail_ok_an.file_path == trustable_mail

    def test_mail_analysis_is_spam(self):
        assert self.mail_ok_an.is_spam() == 'Ham'

    def test_mail_analysis_get_score(self):
        assert self.mail_ok_an.get_score() == 0.0
