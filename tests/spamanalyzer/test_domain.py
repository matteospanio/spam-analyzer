import socket
import dns.name
from spamanalyzer.domain import Domain


class TestDomain:
    domain = Domain("localhost")
    ip_addr = socket.gethostbyname("localhost")

    def test_from_string(self):
        assert self.domain == Domain.from_string("localhost")

    def test_get_ip_address(self):
        assert self.domain.get_ip_address() == self.ip_addr
        assert Domain.from_ip("inventato").name == dns.name.from_text("unknown")
