"""Common constants, data structures and functions."""

from __future__ import annotations
from hashlib import sha256
from json import dumps
from logging import getLogger
from os.path import getctime
from pathlib import Path
from sys import argv
from typing import IO, NamedTuple


__all__ = [
    'CHUNK_SIZE',
    'LOG_FORMAT',
    'LOGFILE',
    'LOGGER',
    'LOGGER',
    'FileInfo',
    'copy_file',
    'sha256sum'
]


CHUNK_SIZE = 4 * 1024 * 1024    # Four Mebibytes.
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGFILE = Path('synclog.txt')
LOGGER = getLogger(Path(argv[0]).name)


class FileInfo(NamedTuple):
    """Store meta information about a file."""

    sha256sum: str
    ctime: float

    def __bytes__(self) -> bytes:
        """Return JSON-ish bytes."""
        return str(self).encode()

    def __str__(self) -> str:
        """Return a JSON-ish string."""
        return dumps(self.to_json())

    @classmethod
    def from_file(cls, filename: Path | str) -> FileInfo:
        """Create the file info from a file path."""
        return cls(sha256sum(filename), getctime(filename))

    def to_json(self) -> dict:
        """Return JSON-ish dict."""
        return {'sha256sum': self.sha256sum, 'ctime': self.ctime}


def copy_file(src: IO, dst: IO, size: int, chunk_size: int = CHUNK_SIZE):
    """Copy two files."""

    while size > 0:
        size -= (bytes_ := min(size, chunk_size))
        dst.write(src.read(bytes_))


def sha256sum(filename: Path | str) -> str:
    """Return an SHA-256 sum of the specified file."""

    with open(filename, 'rb') as file:
        return sha256(file.read()).hexdigest()
