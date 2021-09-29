"""Private network discovery."""

from ipaddress import IPv4Network, IPv6Network, ip_address
from typing import Iterator

from netifaces import AF_INET, ifaddresses, interfaces  # pylint: disable=E0611

from digsigclt.exceptions import NoAddressFound
from digsigclt.types import IPAddress


__all__ = ['discover_address']


OPENVPN = IPv4Network('10.8.0.0/16')
WIREGUARD = IPv6Network('fd56:1dda:8794:cb90::/64')
NETWORKS = [OPENVPN, WIREGUARD]


def get_addresses() -> Iterator[IPAddress]:
    """Yields available IP networks."""

    for interface in interfaces():
        if addresses := ifaddresses(interface).get(AF_INET):
            for address in addresses:
                yield ip_address(address['addr'])


def discover_address() -> IPAddress:
    """Periodically retry to get an address on the network."""

    if addresses := list(get_addresses()):
        for network in NETWORKS:
            for address in addresses:
                if address in network:
                    return address

    raise NoAddressFound()
