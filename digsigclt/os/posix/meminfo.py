"""Information about system memory."""

from pathlib import Path
from typing import Iterator


__all__ = ["meminfo"]


MEMINFO = Path("/proc/meminfo")


def meminfo() -> Iterator[tuple[str, int | dict[str, str | int]]]:
    """Return memory information."""

    with MEMINFO.open("r", encoding="ascii") as file:
        for line in file:
            if line := line.strip():
                key, value = line.split(":")
                value = value.strip()

                try:
                    value, unit = value.split()
                except ValueError:
                    yield key, int(value)
                else:
                    yield key, {"value": int(value), "unit": unit}
