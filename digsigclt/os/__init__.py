"""OS-independent commands."""

from os import name
from typing import Optional

from digsigclt.common import LOGGER
from digsigclt.os import nt, posix
from digsigclt.types import Screenshot, ServiceState


__all__ = [
    'application_status',
    'beep',
    'checkupdates',
    'disable_application',
    'enable_application',
    'get_service',
    'ping',
    'reboot',
    'screenshot',
    'smartctl',
    'sysinfo',
    'unlock_pacman',
    'uptime'
]


def application_status() -> ServiceState:
    """Checks the status of the digital signage application."""

    if name == 'posix':
        return posix.application_status()

    raise NotImplementedError()


def beep(args: tuple = ()) -> int:
    """Performs a speaker beep to identify the system."""

    if name == 'posix':
        return posix.beep(args=args)

    if name == 'nt':
        if args:
            LOGGER.warning('Ignoring beep arguments on NT system.')

        return nt.beep()

    raise NotImplementedError()


def checkupdates() -> dict:
    """Returns available updates."""

    if name == 'posix':
        return posix.checkupdates()

    raise NotImplementedError()


def disable_application(service: Optional[str] = None) -> int:
    """Disables the digital signage application."""

    if name == 'posix':
        return posix.disable_application(service)

    raise NotImplementedError()


def enable_application(service: Optional[str] = None) -> int:
    """Enables the digital signage application."""

    if name == 'posix':
        return posix.enable_application(service)

    raise NotImplementedError()


def get_service() -> str:
    """Returns the running service."""

    if name == 'posix':
        return posix.get_service()

    raise NotImplementedError()


def ping(host: str, count: int = 4) -> int:
    """Pings a host."""

    if name == 'posix':
        return posix.ping(host, count=count)

    if name == 'nt':
        return nt.ping(host, count=count)

    raise NotImplementedError()


def reboot(delay: int = 0) -> int:
    """Reboots the system."""

    if name == 'posix':
        if delay:
            LOGGER.warning('Ignoring delay argument on POSIX system.')

        return posix.reboot()

    if name == 'nt':
        return nt.reboot(delay=delay)

    raise NotImplementedError()


def screenshot() -> Screenshot:
    """Takes a screenshot."""

    if name == 'posix':
        return posix.screenshot()

    raise NotImplementedError()


def smartctl() -> dict:
    """Checks SMART values of disks."""

    if name == 'posix':
        return posix.device_states()

    raise NotImplementedError()


def sysinfo() -> dict:
    """Returns miscellaneous system information."""

    if name != 'posix':
        raise NotImplementedError()

    return {
        'baytrail': posix.is_baytrail(),
        'cmdline': dict(posix.cmdline()),
        'cpuinfo': list(posix.cpuinfo()),
        'meminfo': dict(posix.meminfo()),
        'smartctl': posix.device_states(),
        'updates': posix.checkupdates(),
        'uptime': posix.uptime()
    }


def unlock_pacman() -> int:
    """Unlocks the package manager."""

    if name == 'posix':
        return posix.unlock_pacman()

    raise NotImplementedError()


def uptime() -> dict:
    """Returns the system uptime."""

    if name == 'posix':
        return posix.uptime()

    raise NotImplementedError()
