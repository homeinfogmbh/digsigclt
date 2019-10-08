"""Miscellaneous functions."""

from ipaddress import IPv4Address

from netifaces import interfaces, ifaddresses, AF_INET

from digsigclt.common import LOGGER
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

    try:
        address = addresses.pop()
    except KeyError:
        raise NetworkError('No terminal network address found.')

    if addresses:
        LOGGER.debug('Found ambiguous addresses for network %s.', network)
        addresses.add(address)

        for index, address in enumerate(addresses, start=1):
            LOGGER.debug('#%i: %s.', index, address)

        raise NetworkError('Ambiguous terminal network addresses found.')

    LOGGER.debug('Found network address %s of network %s.', address, network)
    return address
