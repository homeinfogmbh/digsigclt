"""Reboots the system."""

from digsigclt.exceptions import PackageManagerActive, UnderAdministration
from digsigclt.os.common import command
from digsigclt.os.posix import pacman
from digsigclt.os.posix.common import ADMIN_USERS
from digsigclt.os.posix.common import PACMAN_LOCKFILE
from digsigclt.os.posix.common import logged_in_users
from digsigclt.os.posix.common import sudo


__all__ = ['reboot']


@command()
def reboot() -> list[str]:
    """Reboot the system."""

    if logged_in_users() & ADMIN_USERS:
        raise UnderAdministration()

    if PACMAN_LOCKFILE.exists() or pacman.is_running():
        raise PackageManagerActive()

    return sudo('/usr/bin/systemctl', 'reboot')
