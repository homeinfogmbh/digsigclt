"""OS-independent commands."""

from os import name

from digsigclt.common import LOGGER
from digsigclt.os import nt, posix


__all__ = [
    'application_status',
    'beep',
    'checkupdates',
    'disable_application',
    'enable_application',
    'ping',
    'reboot',
    'smartctl',
    'unlock_pacman',
    'uptime'
]


def application_status():
    """Checks the status of the digital signage application."""

    if name == 'posix':
        return posix.application_status()

    raise NotImplementedError()


def beep(args=None):
    """Performs a speaker beep to identify the system."""

    if name == 'posix':
        return posix.beep(args=args)

    if name == 'nt':
        if args:
            LOGGER.warning('Ignoring beep arguments on NT system.')

        return nt.beep()

    raise NotImplementedError()


def checkupdates():
    """Returns available updates."""

    if name == 'posix':
        return posix.checkupdates()

    raise NotImplementedError()


def disable_application():
    """Disables the digital signage application."""

    if name == 'posix':
        return posix.disable_application()

    raise NotImplementedError()


def enable_application():
    """Enables the digital signage application."""

    if name == 'posix':
        return posix.enable_application()

    raise NotImplementedError()


def ping(host, count=4):
    """Pings a host."""

    if name == 'posix':
        return posix.ping(host, count=count)

    if name == 'nt':
        return nt.ping(host, count=count)

    raise NotImplementedError()


def reboot(delay=0):
    """Reboots the system."""

    if name == 'posix':
        if delay:
            LOGGER.warning('Ignoring delay argument on POSIX system.')

        return posix.reboot()

    if name == 'nt':
        return nt.reboot(delay=delay)

    raise NotImplementedError()


def smartctl():
    """Checks SMART values of disks."""

    if name == 'posix':
        return posix.device_states()

    raise NotImplementedError()


def unlock_pacman():
    """Unlocks the package manager."""

    if name == 'posix':
        return posix.unlock_pacman()

    raise NotImplementedError()


def uptime():
    """Returns the system uptime."""

    if name == 'posix':
        return posix.uptime()

    raise NotImplementedError()
