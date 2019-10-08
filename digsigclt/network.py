"""Miscellaneous functions."""

from ipaddress import IPv4Address

from netifaces import interfaces, ifaddresses, AF_INET

from digsigclt.common import TERMINAL_NETWORK
from digsigclt.exceptions import NetworkError


__all__ = ['terminal_network_address']


def ipv4addresses():
    """Yields IP addresses of all network interfaces."""

    for interface in interfaces():
        for ipv4config in ifaddresses(interface).get(AF_INET, ()):
            yield IPv4Address(ipv4config['addr'])


def terminal_network_addresses():
    """Yields addresses of the private terminal network."""

    for ipv4address in ipv4addresses():
        if ipv4address in TERMINAL_NETWORK:
            yield ipv4address


def terminal_network_address():
    """Returns the address of the private terminal network."""

    addresses = set(terminal_network_addresses())

    if not addresses:
        raise NetworkError('No terminal network address found.')

    if len(addresses) > 1:
        raise NetworkError('Ambiguous terminal network addresses found.')

    return addresses.pop()
