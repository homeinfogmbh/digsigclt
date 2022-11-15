"""Custom types for type hints."""

from __future__ import annotations
from contextlib import suppress
from enum import Enum, auto
from ipaddress import IPv4Address, IPv6Address
from json import dumps
from typing import Iterator, NamedTuple, Sequence


__all__ = [
    'Application',
    'ApplicationMode',
    'Command',
    'IPAddress',
    'Manifest',
    'Payload',
    'ResponseContent',
    'Screenshot',
    'Socket'
]


IPAddress = IPv4Address | IPv6Address
Manifest = Iterator[tuple[list[str], str]]
Payload = None | bytes | str | dict | list | int | float


class ApplicationMode(int, Enum):
    """Application modes."""

    PRODUCTIVE = auto()
    INSTALLATION_INSTRUCTIONS = auto()
    NOT_CONFIGURED = auto()
    OFF = auto()


class Application(NamedTuple):
    """Application types."""

    name: str
    mode: ApplicationMode
    unit: str | None

    def to_json(self) -> dict[str, str]:
        """Return a JSON-ish dict."""
        return {
            'name': self.name,
            'mode': self.mode.name,
            'unit': self.unit
        }


class Command(NamedTuple):
    """Command wrapper for command chaining with metadata."""

    command: Sequence[str]
    crucial: bool = True
    exit_ok: set[int] = frozenset()


class ResponseContent(NamedTuple):
    """A HTTP response content."""

    payload: bytes
    content_type: str

    @classmethod
    def from_payload(
            cls,
            payload: Payload,
            *,
            content_type: str | None = None
    ) -> ResponseContent:
        """Create response content from the given payload and content type."""
        if payload is None or isinstance(payload, (dict, list)):
            return cls(
                dumps(payload).encode(),
                content_type or 'application/json'
            )

        if isinstance(payload, str):
            content_type = content_type or 'text/plain'

        with suppress(AttributeError):
            payload = payload.encode()

        return cls(payload, content_type)


class Screenshot(NamedTuple):
    """Screenshot data."""

    bytes: bytes
    content_type: str


class Socket(NamedTuple):
    """An IP socket."""

    ip_address: IPAddress
    port: int
