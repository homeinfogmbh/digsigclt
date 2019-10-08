"""Miscellaneous functions."""

from ipaddress import IPv4Address, IPv6Address
from socket import getaddrinfo, gethostname

from digsigclt.common import TERMINAL_NETWORK
from digsigclt.exceptions import NetworkError


__all__ = ['terminal_network_address']


def ipaddresses():
    """Yields IP addresses of this system."""

    for info in getaddrinfo(gethostname(), None):
        ipaddress = info[4][0]

        try:
            yield IPv6Address(ipaddress)
        except ValueError:
            yield IPv4Address(ipaddress)


def terminal_network_addresses():
    """Yields addresses of the private terminal network."""

    for address in ipaddresses():
        if address in TERMINAL_NETWORK:
            yield address


def terminal_network_address():
    """Returns the address of the private terminal network."""

    addresses = set(terminal_network_addresses())

    if not addresses:
        raise NetworkError('No terminal network address found.')

    if len(addresses) > 1:
        raise NetworkError('Ambiguous terminal network addresses found.')

    return addresses.pop()
