"""Common request handler-related functions."""

from contextlib import suppress
from json import dumps
from pathlib import Path

from digsigclt.lock import Locked
from digsigclt.sync import gen_manifest
from digsigclt.types import Payload, ResponseContent
from digsigclt.request_handler.common import LOCK


__all__ = ['format_response', 'get_manifest']


def format_response(payload: Payload, content_type: str) -> ResponseContent:
    """Detects the content type and formats the HTTP payload accordingly."""

    if payload is None or isinstance(payload, (dict, list)):
        payload = dumps(payload)
        content_type = content_type or 'application/json'
    elif isinstance(payload, str):
        content_type = content_type or 'text/plain'

    with suppress(AttributeError):
        payload = payload.encode()

    return ResponseContent(payload, content_type)


def get_manifest(directory: Path, chunk_size: int) -> list | None:
    """Returns the manifest."""

    with suppress(Locked):
        with LOCK:
            return list(gen_manifest(directory, chunk_size=chunk_size))

    return None
