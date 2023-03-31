"""Network statistics."""

from pathlib import Path


__all__ = ['netstats']


BASEDIR = Path('/sys/class/net')


def netstats() -> dict[str, dict[str, int]]:
    """Return network statistics for each interface."""

    return {
        path.name: dict(interface_stats(path))
        for path in BASEDIR.iterdir()
    }


def interface_stats(path: Path) -> dict[str, int]:
    """Yield network statistics for the given interface."""

    return {
        file.name: read_file(path / file)
        for file in path.joinpath('statistics').iterdir()
        if file.is_file()
    }


def read_file(path: Path) -> int:
    """Read the integer value of the given file,
    iff applicable, else file content as str.
    """

    with path.open('r', encoding='utf-8') as file:
        return int(file.read())
