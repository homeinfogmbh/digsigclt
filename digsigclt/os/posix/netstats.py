"""Network statistics."""

from contextlib import suppress
from pathlib import Path
from typing import Iterator


__all__ = ['netstats']


BASEDIR = Path('/sys/class/net')


def netstats() -> dict[str, dict[str, int | str]]:
    """Return network statistics for each interface."""

    return {
        path.name: dict(interface_stats(path))
        for path in BASEDIR.iterdir()
    }


def interface_stats(path: Path) -> Iterator[tuple[str, int | str]]:
    """Yield network statistics for the given interface."""

    for file in filter(Path.is_file, path.iterdir()):
        with suppress(OSError):
            yield file.name, read_file(path / file)


def read_file(path: Path) -> int | str:
    """Read the integer value of the given file,
    iff applicable, else file content as str.
    """

    with path.open('r', encoding='utf-8') as file:
        content = file.read()

    with suppress(ValueError):
        return int(content)

    with suppress(ValueError):
        return int(content, 16)

    return content
