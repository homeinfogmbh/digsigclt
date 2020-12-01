"""File I/O functions."""

from typing import IO

from digsigclt.common import CHUNK_SIZE


__all__ = ['copy_file']


def copy_file(src: IO, dst: IO, size: int, chunk_size: int = CHUNK_SIZE):
    """Copies two files."""

    while size > 0:
        size -= (bytes := min(size, chunk_size))    # pylint: disable=W0622
        dst.write(src.read(bytes))
