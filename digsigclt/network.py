"""Network discovery."""

from ipaddress import IPv4Address
from time import sleep

from netifaces import AF_INET, interfaces, ifaddresses  # pylint: disable=E0611

from digsigclt.common import LOGGER
from digsigclt.exceptions import NoAddressFound, AmbiguousAddressesFound


__all__ = ['retry_get_address']


def ipv4addresses():
    """Yields IP addresses of all network interfaces."""

    for interface in interfaces():
        for ipv4config in ifaddresses(interface).get(AF_INET, ()):
            yield IPv4Address(ipv4config['addr'])


def get_address(networks):
    """Returns a configured address that is in the given network."""

    system_addresses = set(ipv4addresses())

    for network in networks:
        addresses = {addr for addr in system_addresses if addr in network}

        try:
            address = addresses.pop()
        except KeyError:
            LOGGER.info('No address found on network %s.', network)
            continue

        if addresses:
            addresses.add(address)
            raise AmbiguousAddressesFound(network, addresses)

        LOGGER.debug('Found address %s of network %s.', address, network)
        return address

    raise NoAddressFound()


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
