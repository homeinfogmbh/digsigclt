"""Pacman related commands."""

from digsigclt.exceptions import PackageManagerActive
from digsigclt.os.common import command
from digsigclt.os.posix.common import sudo


__all__ = ['is_running', 'unlock']


@command(as_bool=True)
def is_running() -> list[str]:
    """Checks if pacman is running."""

    return ['/usr/bin/pidof', 'pacman']


@command()
def unlock() -> list[str]:
    """Unlocks the package manager."""

    if is_running():
        raise PackageManagerActive()

    return sudo('/usr/bin/rm', '-f', '/var/lib/pacman/db.lck')
