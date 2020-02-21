"""POSIX system commands."""

from json import loads
from pathlib import Path
from subprocess import check_output


__all__ = [
    'ADMIN_USERS',
    'LIST_SESSIONS_JSON',
    'PACMAN_LOCKFILE',
    'sudo',
    'systemctl',
    'list_sessions',
    'logged_in_users'
]


ADMIN_USERS = {'homeinfo'}
LIST_SESSIONS_JSON = ('/usr/bin/loginctl', 'list-sessions', '-o', 'json')
PACMAN_LOCKFILE = Path('/var/lib/pacman/db.lck')


def sudo(command, *args):
    """Returns the command ran as sudo."""

    if args:
        return ('/usr/bin/sudo', command) + args

    if isinstance(command, str):
        return ('/usr/bin/sudo', command)

    return ('/usr/bin/sudo',) + command


def systemctl(*args):
    """Runs systemctl with the respective arguments."""

    return ('/usr/bin/systemctl',) + args


def list_sessions():
    """Lists the currently active sessions."""

    # pylint: disable=E1123
    return loads(check_output(LIST_SESSIONS_JSON, text=True))


def logged_in_users():
    """Returns a set of users with an active session."""

    return {session['user'] for session in list_sessions()}
