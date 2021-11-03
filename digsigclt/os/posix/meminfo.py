"""Information about system memory."""

from pathlib import Path
from typing import Union


__all__ = ['meminfo']


MEMINFO = Path('/proc/meminfo')


def meminfo() -> dict[str, Union[int, dict[str, Union[str, int]]]]:
    """Returns memory information."""

    result = {}

    with MEMINFO.open('r', encoding='ascii') as file:
        for line in file:
            if line := line.strip():
                key, value = line.split(':')
                value = value.strip()

                try:
                    value, unit = value.split()
                except ValueError:
                    result[key] = int(value)
                else:
                    result[key] = {'value': int(value), 'unit': unit}

    return result
