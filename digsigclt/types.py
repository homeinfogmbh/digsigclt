"""Custom types for type hints."""

from ipaddress import IPv4Address, IPv6Address
from typing import Iterator, NamedTuple


__all__ = [
    'ApplicationVersion',
    'IPAddress',
    'Manifest',
    'Payload',
    'Screenshot',
    'ServiceState',
    'Socket'
]


IPAddress = IPv4Address | IPv6Address
Manifest = Iterator[tuple[list[str], str]]
Payload = None | bytes | str | dict | list | int | float


class ApplicationVersion(NamedTuple):
    """Application version."""

    name: str
    service: str


class Screenshot(NamedTuple):
    """Represents screenshot data."""

    bytes: bytes
    content_type: str


class ServiceState(NamedTuple):
    """System service state."""

    running: set[str]
    enabled: set[str]

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {
            'enabled': sorted(self.enabled),
            'running': sorted(self.running)
        }


class Socket(NamedTuple):
    """An IP socket."""

    ip_address: IPAddress
    port: int
