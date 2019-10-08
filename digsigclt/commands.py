"""System adminstration command handling."""

from json import loads
from os import name
from pathlib import Path
from subprocess import CalledProcessError, check_call, check_output

from digsigclt.common import LOGGER, ServiceState
from digsigclt.exceptions import UnderAdministration, PackageManagerActive


__all__ = [
    'beep',
    'reboot',
    'unlock_pacman',
    'enable_application',
    'disable_application',
    'application_status'
]


_ADMIN_USERS = {'homeinfo'}
_APPLICATION_SERVICE = 'application.service'
_LIST_SESSIONS_JSON = ('/usr/bin/loginctl', 'list-sessions', '-o', 'json')
_PACMAN_LOCKFILE = Path('/var/lib/pacman/db.lck')
_REBOOT_WINDOWS = ('C:\\Windows\\System32\\shutdown.exe', '/r')


def _sudo(command, *args):
    """Returns the command ran as sudo."""

    if args:
        return ('/usr/bin/sudo', command) + args

    if isinstance(command, str):
        return ('/usr/bin/sudo', command)

    return ('/usr/bin/sudo',) + command


_REBOOT_POSIX = _sudo('/usr/bin/systemctl', 'reboot')
_UNLOCK_PACMAN = _sudo('/usr/bin/rm', '-f', '/var/lib/pacman/db.lck')


def _systemctl(*args):
    """Runs systemctl with the respective arguments."""

    return ('/usr/bin/systemctl',) + args


_ENABLE_APPLICATION = _sudo(_systemctl(
    'enable', '--now', _APPLICATION_SERVICE))
_DISABLE_APPLICATION = _sudo(_systemctl(
    'disable', '--now', _APPLICATION_SERVICE))
_APPLICATION_ENABLED = _systemctl('is-enabled', _APPLICATION_SERVICE)
_APPLICATION_RUNNING = _systemctl('is-active', _APPLICATION_SERVICE)


def _list_serssions():
    """Lists the currently active sessions."""

    text = check_output(_LIST_SESSIONS_JSON, text=True)
    return loads(text)


def _logged_in_users():
    """Returns a set of users with an active session."""

    return {session['user'] for session in _list_serssions()}


def _pacman_running():
    """Checks if pacman is running."""

    try:
        check_call(('/usr/bin/pidof', 'pacman'))
    except CalledProcessError:
        return False

    return True


def beep(args=None):
    """Performs a speaker beep to identify the system."""

    if name == 'posix':
        if args:
            command = ['/usr/bin/beep'] + args
        else:
            command = '/usr/bin/beep'

        return check_call(command)

    if name == 'nt':
        if args:
            LOGGER.warning('Ignoring beep arguments on NT system.')

        return check_call('@echo \x07', shell=True)

    raise NotImplementedError()


def reboot(delay=0):
    """Reboots the system."""

    if name == 'posix':
        if _logged_in_users() & _ADMIN_USERS:
            raise UnderAdministration()

        if _PACMAN_LOCKFILE.exists() or _pacman_running():
            raise PackageManagerActive()

        if delay:
            LOGGER.warning('Ignoring delay argument on POSIX system.')

        return check_call(_REBOOT_POSIX)

    if name == 'nt':
        command = _REBOOT_WINDOWS

        if delay is not None:
            command += ('/t', str(delay))

        return check_call(command)

    raise NotImplementedError()


def unlock_pacman():
    """Unlocks the package manager."""

    if name != 'posix':
        raise NotImplementedError()

    if _pacman_running():
        raise PackageManagerActive()

    return check_call(_UNLOCK_PACMAN)


def enable_application():
    """Enables the digital signage application."""

    if name != 'posix':
        raise NotImplementedError()

    return check_call(_ENABLE_APPLICATION)


def disable_application():
    """Disables the digital signage application."""

    if name != 'posix':
        raise NotImplementedError()

    return check_call(_DISABLE_APPLICATION)


def application_status():
    """Enables the digital signage application."""

    if name != 'posix':
        raise NotImplementedError()

    try:
        check_call(_APPLICATION_ENABLED)
    except CalledProcessError:
        enabled = False
    else:
        enabled = True

    try:
        check_call(_APPLICATION_RUNNING)
    except CalledProcessError:
        running = False
    else:
        running = True

    return ServiceState(enabled, running)
