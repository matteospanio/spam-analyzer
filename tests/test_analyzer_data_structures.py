from spamdetector.analyzer.data_structures import Domain, MailAnalysis, MailAnalyzer

class TestDomainMethods:
    
    domain = Domain('google.com')

    def test_from_string(self):
        assert self.domain == Domain.from_string('google.com')
        
    def test_from_ip(self):
        assert self.domain == Domain.from_ip('142.250.180.174')

    def test_get_ip_address(self):
        assert self.domain.get_ip_address() == '142.250.180.174'