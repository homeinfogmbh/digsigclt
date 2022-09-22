"""Common constants."""

from contextlib import suppress
from pathlib import Path

from digsigclt.lock import Lock, Locked
from digsigclt.sync import gen_manifest


__all__ = ['LOCK', 'get_manifest']


LOCK = Lock()


def get_manifest(directory: Path, chunk_size: int) -> list | None:
    """Returns the manifest."""

    with suppress(Locked):
        with LOCK:
            return list(gen_manifest(directory, chunk_size=chunk_size))

    return None
