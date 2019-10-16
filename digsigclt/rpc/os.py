"""OS-independent commands."""

from os import name

from digsigclt.common import LOGGER
from digsigclt.rpc import nt, posix


__all__ = [
    'beep',
    'reboot',
    'unlock_pacman',
    'enable_application',
    'disable_application',
    'application_status'
]


def beep(args=None):
    """Performs a speaker beep to identify the system."""

    if name == 'posix':
        return posix.beep(args=args)

    if name == 'nt':
        if args:
            LOGGER.warning('Ignoring beep arguments on NT system.')

        nt.beep()

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


def unlock_pacman():
    """Unlocks the package manager."""

    if name != 'posix':
        raise NotImplementedError()

    return posix.unlock_pacman()


def enable_application():
    """Enables the digital signage application."""

    if name != 'posix':
        raise NotImplementedError()

    return posix.enable_application()


def disable_application():
    """Disables the digital signage application."""

    if name != 'posix':
        raise NotImplementedError()

    return posix.disable_application()


def application_status():
    """Enables the digital signage application."""

    if name != 'posix':
        raise NotImplementedError()

    return posix.application_status()

