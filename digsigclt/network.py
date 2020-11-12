"""Private network discovery."""

from ipaddress import IPv4Network, ip_address

from netifaces import AF_INET, ifaddresses, interfaces  # pylint: disable=E0611

from digsigclt.exceptions import NoAddressFound
from digsigclt.types import IPAddress, IPAddresses


__all__ = ['discover_address']


OPENVPN = IPv4Network('10.8.0.0/16')
WIREGUARD = IPv4Network('10.10.0.0/16')
NETWORKS = [OPENVPN, WIREGUARD]


def get_addresses() -> IPAddresses:
    """Yields available IP networks."""

    for interface in interfaces():
        for address in ifaddresses(interface).get(AF_INET, []):
            yield ip_address(address['addr'])


def discover_address() -> IPAddress:
    """Periodically retry to get an address on the network."""

    for network in NETWORKS:
        for address in get_addresses():
            if address in network:
                return address

    raise NoAddressFound()
