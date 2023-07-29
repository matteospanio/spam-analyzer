import socket

import dns.name
import pytest

from spamanalyzer.domain import Domain, DomainRelation


class TestDomain:
    domain = Domain("localhost")
    ip_addr = socket.gethostbyname("localhost")

    def test_from_string(self):
        assert self.domain == Domain.from_string("localhost")

    @pytest.mark.anyio
    async def test_get_ip_address(self):
        assert (await self.domain.get_ip_address()) == self.ip_addr
        assert (await Domain.from_ip("inventato")).name == dns.name.from_text("unknown")

    def test_equals(self):
        assert self.domain == self.domain
        assert self.domain != Domain.from_string("inventato")
        with pytest.raises(TypeError):
            assert self.domain == "localhost"

    def test_is_subdomain(self):
        assert self.domain.is_subdomain(Domain.from_string("localhost"))
        assert not self.domain.is_subdomain(Domain.from_string("inventato"))
        assert Domain.from_string("it.localhost").is_subdomain(self.domain)
        with pytest.raises(TypeError):
            assert self.domain.is_subdomain("localhost")  # type: ignore

    def test_is_superdomain(self):
        assert self.domain.is_superdomain(Domain.from_string("it.localhost"))
        assert self.domain.is_superdomain(Domain.from_string("localhost"))
        assert not self.domain.is_superdomain(Domain.from_string("inventato"))
        with pytest.raises(TypeError):
            assert self.domain.is_superdomain("localhost")  # type: ignore

    def test_relation(self):
        assert (self.domain.relation(
            Domain.from_string("localhost")) == DomainRelation.EQUAL)
        assert (self.domain.relation(
            Domain.from_string("it.localhost")) == DomainRelation.SUPERDOMAIN)
        assert (self.domain.relation(
            Domain.from_string("inventato")) == DomainRelation.DIFFERENT)
        assert (Domain.from_string("it.localhost").relation(
            self.domain) == DomainRelation.SUBDOMAIN)
