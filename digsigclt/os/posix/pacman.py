"""Pacman related commands."""

from subprocess import PIPE, CompletedProcess, run
from digsigclt.exceptions import PackageManagerActive
from digsigclt.os.common import command
from digsigclt.os.posix.common import sudo


__all__ = ['is_running', 'pacman', 'unlock']


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


def pacman(*args: str) -> CompletedProcess:
    """Runs pacman."""

    return run(
        ['/usr/bin/pacman', *args],
        check=True,
        text=True,
        stderr=PIPE,
        stdout=PIPE
    )
