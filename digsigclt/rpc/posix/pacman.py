"""Pacman related commands."""

from subprocess import CalledProcessError, check_call

from digsigclt.exceptions import PackageManagerActive
from digsigclt.rpc.posix.common import sudo


__all__ = ['is_running', 'unlock']


UNLOCK = sudo('/usr/bin/rm', '-f', '/var/lib/pacman/db.lck')


def is_running():
    """Checks if pacman is running."""

    try:
        check_call(('/usr/bin/pidof', 'pacman'))
    except CalledProcessError:
        return False

    return True


def unlock():
    """Unlocks the package manager."""

    if is_running():
        raise PackageManagerActive()

    return check_call(UNLOCK)
