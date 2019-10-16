"""POSIX system commands."""

from json import loads
from pathlib import Path
from subprocess import CalledProcessError, check_call, check_output

from digsigclt.common import ServiceState
from digsigclt.exceptions import UnderAdministration, PackageManagerActive


__all__ = [
    'beep',
    'reboot',
    'unlock_pacman',
    'enable_application',
    'disable_application',
    'application_status'
]


ADMIN_USERS = {'homeinfo'}
APPLICATION_SERVICE = 'application.service'
LIST_SESSIONS_JSON = ('/usr/bin/loginctl', 'list-sessions', '-o', 'json')
PACMAN_LOCKFILE = Path('/var/lib/pacman/db.lck')


def sudo(command, *args):
    """Returns the command ran as sudo."""

    if args:
        return ('/usr/bin/sudo', command) + args

    if isinstance(command, str):
        return ('/usr/bin/sudo', command)

    return ('/usr/bin/sudo',) + command


REBOOT = sudo('/usr/bin/systemctl', 'reboot')
UNLOCK_PACMAN = sudo('/usr/bin/rm', '-f', '/var/lib/pacman/db.lck')


def systemctl(*args):
    """Runs systemctl with the respective arguments."""

    return ('/usr/bin/systemctl',) + args


ENABLE_APPLICATION = sudo(systemctl('enable', '--now', APPLICATION_SERVICE))
DISABLE_APPLICATION = sudo(systemctl('disable', '--now', APPLICATION_SERVICE))
APPLICATION_ENABLED = systemctl('is-enabled', APPLICATION_SERVICE)
APPLICATION_RUNNING = systemctl('is-active', APPLICATION_SERVICE)


def list_serssions():
    """Lists the currently active sessions."""

    return loads(check_output(LIST_SESSIONS_JSON, text=True))


def logged_in_users():
    """Returns a set of users with an active session."""

    return {session['user'] for session in list_serssions()}


def pacman_running():
    """Checks if pacman is running."""

    try:
        check_call(('/usr/bin/pidof', 'pacman'))
    except CalledProcessError:
        return False

    return True


def beep(args=None):
    """Performs a speaker beep to identify the system."""

    command = ['/usr/bin/beep']

    if args:
        command += args

    return check_call(command)


def reboot():
    """Reboots the system."""

    if logged_in_users() & ADMIN_USERS:
        raise UnderAdministration()

    if PACMAN_LOCKFILE.exists() or pacman_running():
        raise PackageManagerActive()

    return check_call(REBOOT)


def unlock_pacman():
    """Unlocks the package manager."""

    if pacman_running():
        raise PackageManagerActive()

    return check_call(UNLOCK_PACMAN)


def enable_application():
    """Enables the digital signage application."""

    return check_call(ENABLE_APPLICATION)


def disable_application():
    """Disables the digital signage application."""

    return check_call(DISABLE_APPLICATION)


def application_status():
    """Enables the digital signage application."""

    try:
        check_call(APPLICATION_ENABLED)
    except CalledProcessError:
        enabled = False
    else:
        enabled = True

    try:
        check_call(APPLICATION_RUNNING)
    except CalledProcessError:
        running = False
    else:
        running = True

    return ServiceState(enabled, running)
