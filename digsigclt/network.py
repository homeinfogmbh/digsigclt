"""Private network discovery."""

from ipaddress import ip_address
from socket import AF_INET, SOCK_DGRAM, socket
from subprocess import CalledProcessError
from time import sleep

from digsigclt.common import LOGGER
from digsigclt.exceptions import NoAddressFound
from digsigclt.os import ping
from digsigclt.types import IPAddress


__all__ = ['discover_address']


IP_ADDRESS = '10.8.0.1'
PORT = 80
SOCKET = (IP_ADDRESS, PORT)


def get_address() -> IPAddress:
    """Returns a configured address that is in the given network."""

    # Ping address first to determine that a route exists.
    try:
        ping(IP_ADDRESS)
    except CalledProcessError:
        raise NoAddressFound() from None

    # Get local IP address from socket connection.
    with socket(AF_INET, SOCK_DGRAM) as sock:
        try:
            sock.connect(SOCKET)
        except OSError:
            raise NoAddressFound() from None

        address, port = sock.getsockname()

    LOGGER.debug('Got IP address %s on port %i.', address, port)
    return ip_address(address)


def discover_address(interval: int = 1, retries: int = 60) -> IPAddress:
    """Periodically retry to get an address on the network."""

    for tries in range(retries):
        try:
            return get_address()
        except NoAddressFound:
            sleep(interval)

        if time := interval * tries:
            LOGGER.warning('No address discovered after %i seconds.', time)

    raise NoAddressFound()
