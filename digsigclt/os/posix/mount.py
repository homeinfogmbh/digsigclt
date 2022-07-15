"""Check mount points."""

from __future__ import annotations
from contextlib import suppress
from os import linesep
from pathlib import Path
from re import fullmatch
from subprocess import check_output
from typing import Any, Iterator, NamedTuple


__all__ = ['efi_mounted_as_boot', 'mount', 'root_mounted_ro']


EFI_PARTITION = Path('/dev/disk/by-label/EFI')
BOOT = Path('/boot')
MOUNT_REGEX = r'(.+) on (.+) type (.+) \((.+)\)'


class Mount(NamedTuple):
    """Representation of mountpoints."""

    what: str
    where: Path
    type: str
    flags: list[str]

    @classmethod
    def from_string(cls, string: str) -> Mount:
        """Creates a mount instance from a string."""
        if (match := fullmatch(MOUNT_REGEX, string)) is None:
            raise ValueError('Invalid mount value:', string)

        what, where, typ, flags = match.groups()
        return cls(what, Path(where), typ, flags.split(','))

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-ish dict."""
        return {
            'what': self.what,
            'where': str(self.where),
            'type': self.type,
            'flags': self.flags
        }


def efi_mounted_as_boot() -> bool:
    """Checks whether the EFI partition is mounted on /boot.
    Also return True if not applicable.
    """

    return not efi_not_mounted_as_boot()


def efi_not_mounted_as_boot() -> bool:
    """Return True iff there is an EFI partition
    to be mounted on /boot, but it is not.
    """

    return EFI_PARTITION.is_block_device() and not BOOT.is_mount()


def mount() -> Iterator[Mount]:
    """Yields mounts on the system."""

    for line in check_output('mount', text=True).split(linesep):
        with suppress(ValueError):
            yield Mount.from_string(line)


def root_mounted_ro() -> bool | None:
    """Check whether / is mounted read-only."""

    for mnt in mount():
        if mnt.where == Path('/'):
            return 'ro' in mnt.flags

    return None
