"""Common functions."""

from hashlib import sha256
from os.path import getctime
from pathlib import Path
from typing import Union


__all__ = ['fileinfo', 'sha256sum']


def fileinfo(filename: Union[Path, str]) -> dict:
    """Returns JSON-ish file info."""

    return {
        'sha256sum': sha256sum(filename),
        'ctime': getctime(filename)
    }


def sha256sum(filename: Union[Path, str]) -> str:
    """Returns a SHA-256 sum of the specified file."""

    with open(filename, 'rb') as file:
        return sha256(file.read()).hexdigest()
