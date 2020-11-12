"""Custom types for type hints."""

from ipaddress import IPv4Address, IPv6Address
from typing import Iterable, NamedTuple, Union


__all__ = [
    'BoolNa',
    'IPAddress',
    'IPAddresses',
    'Payload',
    'Screenshot',
    'ServiceState',
    'Socket'
]


BoolNa = Union[bool, None]
IPAddress = Union[IPv4Address, IPv6Address]
IPAddresses = Iterable[IPAddress]
Payload = Union[None, bytes, str, dict, list, int, float]


class Screenshot(NamedTuple):
    """Represents screenshot data."""

    bytes: bytes
    content_type: str


class ServiceState(NamedTuple):
    """System service state."""

    running: bool
    enabled: bool

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {'enabled': self.enabled, 'running': self.running}


class Socket(NamedTuple):
    """An IP socket."""

    ip_address: IPAddress
    port: int

    def compat(self):
        """Returns a tuple with the IP address converted into a str."""
        return (str(self.ip_address), self.port)
