"""Private network discovery."""

from ipaddress import ip_address
from socket import AF_INET, SOCK_DGRAM, socket
from time import sleep

from digsigclt.common import LOGGER
from digsigclt.exceptions import NoAddressFound


__all__ = ['discover_address']


IP_ADDRESS = '10.8.0.1'
PORT = 80
SOCKET = (IP_ADDRESS, PORT)


def get_address():
    """Returns a configured address that is in the given network."""

    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.connect(SOCKET)
        address, port = sock.getsockname()

    LOGGER.debug('Got IP address %s on port %i.', address, port)
    return ip_address(address)


def discover_address(interval=1, retries=60):
    """Periodically retry to get an address on the network."""

    for tries in range(retries):
        try:
            address = get_address()
        except NoAddressFound:
            sleep(interval)
            continue

        time = interval * tries
        LOGGER.info('Discovered address %s after %i seconds.', address, time)
        return address

    raise NoAddressFound()
