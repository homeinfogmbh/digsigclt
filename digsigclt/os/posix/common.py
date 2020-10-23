"""POSIX system commands."""

from json import loads
from pathlib import Path
from subprocess import check_output


__all__ = [
    'ADMIN_USERS',
    'LIST_SESSIONS_JSON',
    'PACMAN_LOCKFILE',
    'SCROT',
    'sudo',
    'systemctl',
    'list_sessions',
    'logged_in_users'
]


ADMIN_USERS = {'homeinfo'}
SUDO = '/usr/bin/sudo'
SYSTEMCTL = '/usr/bin/systemctl'
LOGINCTL = '/usr/bin/loginctl'
LIST_SESSIONS_JSON = (LOGINCTL, 'list-sessions', '-o', 'json')
PACMAN_LOCKFILE = Path('/var/lib/pacman/db.lck')
SCROT = '/usr/bin/scrot'


def sudo(command: str, *args: str) -> tuple:
    """Returns the command ran as sudo."""

    if args:
        return (SUDO, command) + args

    if isinstance(command, str):
        return (SUDO, command)

    return (SUDO,) + tuple(command)


def systemctl(*args: str) -> tuple:
    """Runs systemctl with the respective arguments."""

    return (SYSTEMCTL,) + args


def list_sessions() -> list:
    """Lists the currently active sessions."""

    # pylint: disable=E1123
    return loads(check_output(LIST_SESSIONS_JSON, text=True))


def logged_in_users() -> set:
    """Returns a set of users with an active session."""

    return {session['user'] for session in list_sessions()}
