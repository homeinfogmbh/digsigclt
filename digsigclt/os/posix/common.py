"""POSIX system commands."""

from json import loads
from os import linesep
from pathlib import Path
from subprocess import CalledProcessError, check_call, check_output
from typing import Iterable, Iterator


__all__ = [
    'ADMIN_USERS',
    'LIST_SESSIONS_JSON',
    'PACMAN_LOCKFILE',
    'SCROT',
    'sudo',
    'systemctl',
    'journalctl',
    'list_journal',
    'list_sessions',
    'logged_in_users',
    'is_active',
    'is_enabled'
]


ADMIN_USERS = {'homeinfo', 'root'}
SUDO = '/usr/bin/sudo'
SYSTEMCTL = '/usr/bin/systemctl'
JOURNALCTL = '/usr/bin/journalctl'
LOGINCTL = '/usr/bin/loginctl'
LIST_SESSIONS_JSON = (LOGINCTL, 'list-sessions', '-o', 'json')
PACMAN_LOCKFILE = Path('/var/lib/pacman/db.lck')
SCROT = '/usr/bin/scrot'


def sudo(command: str | Iterable[str], *args: str) -> list[str]:
    """Return the command ran as sudo."""

    if isinstance(command, str):
        return [SUDO, command, *args]

    return [SUDO, *command, *args]


def systemctl(command: str, *args: str) -> list[str]:
    """Run systemctl with the respective arguments."""

    return [SYSTEMCTL, command, *args]


def journalctl(unit: str, boot: str | None = None) -> list[str]:
    """Return a journalctl command."""

    command = [JOURNALCTL, '-u', unit, '--output=json', '-b']

    if boot is None:
        return command

    return [*command, boot]


def list_journal(unit: str, boot: str | None = None) -> Iterator[dict]:
    """List the journal of the given unit."""

    if not (lines := check_output(journalctl(unit, boot), text=True)):
        return

    for line in filter(None, lines.split(linesep)):
        yield loads(line)


def list_sessions() -> list[dict[str, str | int]]:
    """List the currently active sessions."""

    return loads(check_output(LIST_SESSIONS_JSON, text=True))


def logged_in_users() -> set[str]:
    """Return a set of users with an active session."""

    return {session['user'] for session in list_sessions()}


def is_enabled(unit: str) -> bool:
    """Check whether the unit is enabled."""

    try:
        check_call(systemctl('is-enabled', unit, '--quiet'))
    except CalledProcessError:
        return False

    return True


def is_active(unit: str) -> bool:
    """Check whether the unit is running."""

    try:
        check_call(systemctl('is-active', unit, '--quiet'))
    except CalledProcessError:
        return False

    return True
