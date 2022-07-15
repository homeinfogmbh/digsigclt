"""Check mount points."""

from __future__ import annotations
from os import linesep
from pathlib import Path
from re import fullmatch
from subprocess import check_output
from typing import Any, Iterator, NamedTuple


__all__ = ['efi_mounted_as_boot', 'mount', 'root_mounted_ro']


EFI_PARTITION = Path('/dev/disk/by-label/EFI')
BOOT = Path('/boot')
MOUNT_REGEX = r'(.+) on (.+) type (.+) \((.+)\)'


class MountPoint(NamedTuple):
    """Representation of mount points."""

    what: str
    where: Path
    type: str
    flags: dict[str, str | int | None]

    @classmethod
    def from_string(cls, string: str) -> MountPoint:
        """Create a mount point from a string."""
        if (match := fullmatch(MOUNT_REGEX, string)) is None:
            raise ValueError('Invalid mount value:', string)

        what, where, typ, flags = match.groups()
        return cls(
            what,
            Path(where),
            typ,
            dict(map(parse_flag, flags.split(',')))
        )

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


def mount() -> Iterator[MountPoint]:
    """Yield mount points on the system."""

    for line in filter(None, check_output('mount', text=True).split(linesep)):
        yield MountPoint.from_string(line)


def root_mounted_ro() -> bool | None:
    """Check whether / is mounted read-only."""

    for mount_point in mount():
        if mount_point.where == Path('/'):
            return 'ro' in mount_point.flags

    return None


def parse_flag(flag: str) -> tuple[str, str | int | None]:
    """Parse a mount flag."""

    try:
        key, value = flag.split('=')
    except ValueError:
        return flag, None

    try:
        return key, int(value)
    except ValueError:
        return key, value
