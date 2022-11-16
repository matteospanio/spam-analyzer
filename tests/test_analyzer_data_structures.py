from spamdetector.analyzer.data_structures import Domain, MailAnalysis, MailAnalyzer

trustable_mail = 'tests/samples/97.47949e45691dd7a024dcfaacef4831461bf5d5f09c85a6e44ee478a5bcaf8539.email'
spam = 'tests/samples/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a.email'

with open('assets/word_blacklist.txt', 'r') as f:
    wordlist = f.read().splitlines()


class TestDomainMethods:
    
    domain = Domain('google.com')

    def test_from_string(self):
        assert self.domain == Domain.from_string('google.com')
        
    def test_from_ip(self):
        assert self.domain == Domain.from_ip('142.250.180.174')

    def test_get_ip_address(self):
        assert self.domain.get_ip_address() == '142.250.180.174'


class TestMailAnalyzer:

    def test_get_domain(self):
        analyzer = MailAnalyzer(wordlist)
        assert analyzer.get_domain(trustable_mail) == Domain('github.com')


class TestMailAnalysis:

    weights = {
        "has_spf": 0.5,
        "has_spf": 1,
        "has_dkim": 0.5,
        "has_dmarc": 0.5,
        "has_mx": 0.5,
        "spam_words_in_subject": 0.5,
        "spam_words": 1,
        "domain_matches": 0.5,
        "forbidden_words_percentage": 0.5,
    }

    analyzer = MailAnalyzer(wordlist)

    mail_ok_an = analyzer.analyze(trustable_mail)

    def test_mail_analysis_type(self):
        assert type(self.mail_ok_an) == MailAnalysis

    def test_mail_analysis_file_path(self):
        assert self.mail_ok_an.file_path == trustable_mail

    def test_mail_analysis_is_spam(self):
        assert self.mail_ok_an.is_spam() == 'Trust'
    
    def test_mail_analysis_get_score(self):
        assert self.mail_ok_an.get_score(self.weights) == 0.0