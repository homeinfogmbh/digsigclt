"""Private network discovery."""

from ipaddress import IPv4Network, IPv6Network, ip_address
from typing import Iterator

from netifaces import AF_INET, AF_INET6, ifaddresses, interfaces

from digsigclt.exceptions import NoAddressFound
from digsigclt.types import IPAddress


__all__ = ['discover_address']


OPENVPN = IPv4Network('10.8.0.0/16')
WIREGUARD = IPv6Network('fd56:1dda:8794:cb90::/64')
NETWORKS = [OPENVPN, WIREGUARD]


def get_addresses() -> Iterator[IPAddress]:
    """Yield available IP addresses."""

    for interface in interfaces():
        if addresses := ifaddresses(interface):
            for ipv4addr in addresses.get(AF_INET, []):
                yield ip_address(ipv4addr['addr'])

            for ipv6addr in addresses.get(AF_INET6, []):
                yield ip_address(ipv6addr['addr'])


def discover_address() -> IPAddress:
    """Periodically retry to get an address on the network."""

    if addresses := list(get_addresses()):
        for network in NETWORKS:
            for address in addresses:
                if address in network:
                    return address

    raise NoAddressFound()
