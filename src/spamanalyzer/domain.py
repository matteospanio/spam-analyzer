import asyncio
import socket
from dataclasses import dataclass
from enum import Enum

import dns.name
import dns.resolver


class DomainRelation(Enum):
    """An enum representing the relation between two domains."""

    SUBDOMAIN = 1
    SUPERDOMAIN = 2
    EQUAL = 3
    DIFFERENT = 4


@dataclass
class Domain:
    """A Domain is a class representing an internet domain, here you can get
    information about the target domain.

    The constructor resolves any domain alias to the real domain name:
    in fact common domain names are aliases for more complex server names
    that would be difficult to remember for common users,
    since there is not a direct method in the `socket` module to resolve domain
    aliases, we use the `gethostbyname` chained with the `gethostbyaddr` methods
    this way makes the instatiation of the class slower, but it is the only way to
    get the real domain name.

    """

    name: dns.name.Name

    @property
    def length(self) -> int:
        return len(self.name.to_text())

    def __init__(self, name: str) -> None:
        self.name = dns.name.from_text(name)

    @staticmethod
    def from_string(domain_str: str):
        """Instantiate a Domain object from string, it is a wrapper of the
        `self.__init__` method.

        Args:
            domain_str (str): a string containing a domain to be parsed

        Returns:
            Domain: the domain obtained from the string

        """
        return Domain(domain_str)

    @staticmethod
    async def from_ip(ip_addr: str):
        """Create a Domain object from an ip address. It translate the ip address
        to its domain name via the `socket.gethostbyaddr` method.

        Args:
            ip_addr (str): the targetted ip address

        Returns:
            Domain: the domain obtained from the ip address

        """
        try:
            domain_name, _, _ = await asyncio.to_thread(socket.gethostbyaddr, ip_addr)
            return Domain(domain_name)
        except Exception:
            return Domain("unknown")

    async def get_ip_address(self) -> str:
        """Translate the domain name to its ip address querying the DNS server.

        Returns:
            str: the ip address of the domain

        Note: this method is async since it performs a network request

        """
        name = await asyncio.to_thread(dns.resolver.resolve, self.name, "A")
        return name[0].to_text()

    def is_subdomain(self, domain: "Domain") -> bool:
        """Is the domain a subdomain of the given domain?

        Args:
            domain (Domain): the reference domain

        Returns:
            bool: True if the domain is a subdomain of the given domain,

        Raises:
            TypeError: if the given object is not a Domain

        Note: a domain is a subdomain of itself

        """
        if not isinstance(domain, Domain):
            raise TypeError("Cannot compare Domain with other types")
        return self.name.is_subdomain(domain.name)

    def is_superdomain(self, domain: "Domain") -> bool:
        """Is the domain a superdomain of the given domain?

        Args:
            domain (Domain): the reference domain

        Returns:
            bool: True if the domain is a superdomain of the given domain,

        Raises:
            TypeError: if the given object is not a Domain

        Note: a domain is a superdomain of itself

        """
        if not isinstance(domain, Domain):
            raise TypeError("Cannot compare Domain with other types")
        return self.name.is_superdomain(domain.name)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Domain):
            return self.name == __o.name
        raise TypeError("Cannot compare Domain with other types")

    def relation(self, domain: "Domain") -> DomainRelation:
        """Define the relation between two domains.

        Args:
            domain (Domain): the domain to compare with

        Returns:
            DomainRelation: the relation between the two domains

        Raises:
            TypeError: if the given object is not a Domain

        """

        if not isinstance(domain, Domain):
            raise TypeError("Cannot compare Domain with other types")

        if self == domain:
            return DomainRelation.EQUAL
        if self.is_subdomain(domain):
            return DomainRelation.SUBDOMAIN
        if self.is_superdomain(domain):
            return DomainRelation.SUPERDOMAIN
        return DomainRelation.DIFFERENT
