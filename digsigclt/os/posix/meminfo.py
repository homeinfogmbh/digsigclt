"""Information about system memory."""

from pathlib import Path
from typing import Iterator, Union


__all__ = ['meminfo']


MEMINFO = Path('/proc/meminfo')


def meminfo() -> Iterator[tuple[str, Union[int, dict[str, Union[str, int]]]]]:
    """Returns memory information."""

    with MEMINFO.open('r', encoding='ascii') as file:
        for line in file:
            if line := line.strip():
                key, value = line.split(':')
                value = value.strip()

                try:
                    value, unit = value.split()
                except ValueError:
                    yield (key, int(value))
                else:
                    yield (key, {'value': int(value), 'unit': unit})
