"""Miscellaneous functions."""

from ipaddress import IPv4Address

from netifaces import interfaces, ifaddresses, AF_INET

from digsigclt.exceptions import NetworkError


__all__ = ['get_address']


def ipv4addresses():
    """Yields IP addresses of all network interfaces."""

    for interface in interfaces():
        for ipv4config in ifaddresses(interface).get(AF_INET, ()):
            yield IPv4Address(ipv4config['addr'])


def get_address(network):
    """Returns a configured address that is in the given network."""

    addresses = {addr for addr in ipv4addresses() if addr in network}

    if not addresses:
        raise NetworkError('No terminal network address found.')

    if len(addresses) > 1:
        raise NetworkError('Ambiguous terminal network addresses found.')

    return addresses.pop()
