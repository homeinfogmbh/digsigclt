"""Common constants, data structures and functions."""

from __future__ import annotations
from hashlib import sha256
from logging import getLogger
from pathlib import Path
from sys import argv
from typing import IO


__all__ = [
    'CHUNK_SIZE',
    'LOG_FORMAT',
    'LOGFILE',
    'LOGGER',
    'LOGGER',
    'copy_file',
    'sha256sum'
]


CHUNK_SIZE = 4 * 1024 * 1024    # Four Mebibytes.
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGFILE = Path('synclog.txt')
LOGGER = getLogger(Path(argv[0]).name)


def copy_file(src: IO, dst: IO, size: int, chunk_size: int = CHUNK_SIZE):
    """Copy two files."""

    while size > 0:
        size -= (bytes_ := min(size, chunk_size))
        dst.write(src.read(bytes_))


def sha256sum(filename: Path | str) -> str:
    """Return an SHA-256 sum of the specified file."""

    with open(filename, 'rb') as file:
        return sha256(file.read()).hexdigest()
