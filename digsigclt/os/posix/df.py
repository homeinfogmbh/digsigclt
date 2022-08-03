"""Wrapper around the df utility to investigate available disk space."""

from __future__ import annotations
from os import linesep
from subprocess import check_output
from typing import Iterator, NamedTuple


__all__ = ['DFEntry', 'df']


DF = '/usr/bin/df'


class DFEntry(NamedTuple):
    """An entry of available disk space."""

    filesystem: str
    blocks: int
    used: int
    available: int
    use_pct: int
    mountpoint: str

    @classmethod
    def from_string(cls, text: str) -> DFEntry:
        """Create a DFEntry from a text string."""
        filesystem, blocks, used, available, use_pct, mountpoint = text.split()
        return cls(
            filesystem,
            int(blocks),
            int(used),
            int(available),
            int(use_pct.rstrip('%')),
            mountpoint
        )

    def to_json(self) -> dict[str, str | int]:
        """Return a JSON-ish dict."""
        return {
            'filesystem': self.filesystem,
            'blocks': self.blocks,
            'used': self.used,
            'available': self.available,
            'use_pct': self.use_pct,
            'mountpoint': self.mountpoint
        }


def get_args(*, local: bool = False, posix: bool = False) -> Iterator[str]:
    """Yield command line arguments."""

    if local:
        yield '-l'

    if posix:
        yield'-P'


def df(*, local: bool = False, posix: bool = False) -> Iterator[DFEntry]:
    """Return information about free disk space."""

    text = check_output([DF, *get_args(local=local, posix=posix)], text=True)

    for line in text.split(linesep)[1:-1]:  # Skip header and empty last line
        yield DFEntry.from_string(line)
