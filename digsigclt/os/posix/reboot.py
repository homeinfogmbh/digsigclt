"""Reboots the system."""

from subprocess import check_call

from digsigclt.exceptions import PackageManagerActive, UnderAdministration
from digsigclt.os.posix.common import ADMIN_USERS
from digsigclt.os.posix.common import PACMAN_LOCKFILE
from digsigclt.os.posix.common import logged_in_users
from digsigclt.os.posix.common import sudo
from digsigclt.os.posix.pacman import is_running as pacman_running


__all__ = ['reboot']


REBOOT = sudo('/usr/bin/systemctl', 'reboot')


def reboot():
    """Reboots the system."""

    if logged_in_users() & ADMIN_USERS:
        raise UnderAdministration()

    if PACMAN_LOCKFILE.exists() or pacman_running():
        raise PackageManagerActive()

    return check_call(REBOOT)
