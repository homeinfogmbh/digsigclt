"""POSIX system commands."""

from json import loads
from pathlib import Path
from subprocess import check_output
from typing import Iterable, Optional, Union


__all__ = [
    'ADMIN_USERS',
    'LIST_SESSIONS_JSON',
    'PACMAN_LOCKFILE',
    'SCROT',
    'sudo',
    'systemctl',
    'journalctl',
    'list_sessions',
    'logged_in_users'
]


ADMIN_USERS = {'homeinfo'}
SUDO = '/usr/bin/sudo'
SYSTEMCTL = '/usr/bin/systemctl'
JOURNALCTL = '/usr/bin/journalctl'
LOGINCTL = '/usr/bin/loginctl'
LIST_SESSIONS_JSON = (LOGINCTL, 'list-sessions', '-o', 'json')
PACMAN_LOCKFILE = Path('/var/lib/pacman/db.lck')
SCROT = '/usr/bin/scrot'


def sudo(command: Union[str, tuple[str]], *args: str) -> Iterable[str]:
    """Returns the command ran as sudo."""

    if isinstance(command, str):
        return (SUDO, command, *args)

    return (SUDO, *command, *args)


def systemctl(command: str, *args: str) -> Iterable[str]:
    """Runs systemctl with the respective arguments."""

    return (SYSTEMCTL, command, *args)


def journalctl(unit: str, boot: Optional[int] = None) -> list[str]:
    """Returns a journalctl command."""

    command = (JOURNALCTL, '-u', unit, '--output=json')

    if boot is None:
        return [*command, '-a']

    return [*command, '-b', str(boot)]


def list_sessions() -> list:
    """Lists the currently active sessions."""

    # pylint: disable=E1123
    return loads(check_output(LIST_SESSIONS_JSON, text=True))


def logged_in_users() -> set[str]:
    """Returns a set of users with an active session."""

    return {session['user'] for session in list_sessions()}
