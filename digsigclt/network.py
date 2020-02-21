"""Miscellaneous functions."""

from ipaddress import IPv4Address
from time import sleep

from netifaces import interfaces, ifaddresses, AF_INET  # pylint: disable=E0611

from digsigclt.common import LOGGER
from digsigclt.exceptions import NoAddressFound, AmbiguousAddressesFound


__all__ = ['retry_get_address']


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
        raise NoAddressFound()

    if addresses:
        addresses.add(address)
        raise AmbiguousAddressesFound(addresses)

    LOGGER.debug('Found network address %s of network %s.', address, network)
    return address


def retry_get_address(network, *, interval=1, retries=60):
    """Periodically retry to get an address on the network."""

    tries = 0

    while tries < retries:
        try:
            address = get_address(network)
        except NoAddressFound:
            tries += 1
            sleep(interval)
        else:
            LOGGER.info(
                'Discovered address %s after %i seconds.', address,
                interval * tries)
            return address

    raise NoAddressFound()
