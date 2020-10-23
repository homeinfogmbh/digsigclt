"""Custom types for type hints."""

from ipaddress import IPv4Address, IPv6Address
from typing import NamedTuple, Tuple, Union


__all__ = ['BoolNa', 'IPAddress', 'Payload', 'Screenshot', 'ServiceState']


BoolNa = Union[bool, None]
IPAddress = Union[IPv4Address, IPv6Address]
Payload = Union[None, bytes, str, dict, list, int, float]
Socket = Tuple[str, int]


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
