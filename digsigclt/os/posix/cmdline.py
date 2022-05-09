"""Parsing of /proc/cmdline."""

from pathlib import Path
from typing import Iterator


__all__ = ['cmdline']


CMDLINE = Path('/proc/cmdline')


def cmdline() -> Iterator[tuple[str, str | None]]:
    """Parse /proc/cmdline into key-value pairs."""

    with CMDLINE.open('r', encoding='ascii') as file:
        for parameter in file.read().strip().split():
            try:
                key, value = parameter.split('=', maxsplit=1)
            except ValueError:
                yield parameter, None
            else:
                yield key, value
