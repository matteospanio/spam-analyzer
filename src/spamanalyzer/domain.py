from dataclasses import dataclass
import socket
import dns.resolver
import dns.name


@dataclass
class Domain:
    """
    A Domain is a class representing an internet domain,
    here you can get information about the target domain

    The constructor resolves any domain alias to the real domain name:
    in fact common domain names are aliases for more complex server names
    that would be difficult to remember for common users,
    since there is not a direct method in the `socket` module to resolve domain
    aliases, we use the `gethostbyname` chained with the `gethostbyaddr` methods
    this way makes the instatiation of the class slower, but it is the only way to
    get the real domain name.
    """

    name: dns.name.Name

    def __init__(self, name: str) -> None:
        # TODO: add a cache for the domain names or find a better way to resolve domain
        #       aliases
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
        Instantiate a Domain object from string,
        it is a wrapper of the `self.__init__` method

        Args:
            domain_str (str): a string containing a domain to be parsed

        Returns:
            Domain: the domain obtained from the string
        """
        return Domain(domain_str)

    @staticmethod
    def from_ip(ip_addr: str):
        """Create a Domain object from an ip address.
        It translate the ip address to its domain name via the
        `socket.gethostbyaddr` method

        Args:
            ip_addr (str): the targetted ip address

        Returns:
            Domain: the domain obtained from the ip address
        """
        try:
            domain_name = socket.gethostbyaddr(ip_addr)[0]
            return Domain(domain_name)
        except Exception:
            return Domain("unknown")

    def get_ip_address(self) -> str:
        """Translate the domain name to its ip address querying the DNS server"""
        return dns.resolver.resolve(self.name, "A")[0].to_text()

    def __eq__(self, __o: object) -> bool:
        (
            result,
            _,
            _,
        ) = self.name.fullcompare(__o.name)
        if isinstance(__o, Domain):
            if result in [1, 2, 3]:
                return True
            return False
        raise TypeError("Cannot compare Domain with other types")
