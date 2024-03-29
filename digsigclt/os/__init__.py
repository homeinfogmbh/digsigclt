"""OS-independent commands."""

from os import name
from typing import Any

from digsigclt.common import LOGGER
from digsigclt.os import nt, posix
from digsigclt.types import Screenshot


__all__ = [
    "application_set_mode",
    "application_status",
    "beep",
    "checkupdates",
    "get_preferred_application",
    "ping",
    "reboot",
    "screenshot",
    "smartctl",
    "sysinfo",
    "unlock_pacman",
    "uptime",
]


def application_set_mode(mode: str) -> int:
    """Enable the digital signage application."""

    if name == "posix":
        return posix.application_set_mode(mode)

    raise NotImplementedError()


def application_status() -> posix.Application:
    """Return the mode of the digital signage application."""

    if name == "posix":
        return posix.application_status()

    raise NotImplementedError()


def beep(args: tuple = ()) -> int:
    """Perform a speaker beep to identify the system."""

    if name == "posix":
        return posix.beep(args=args)

    if name == "nt":
        if args:
            LOGGER.warning("Ignoring beep arguments on NT system.")

        return nt.beep()

    raise NotImplementedError()


def checkupdates() -> dict:
    """Return available updates."""

    if name == "posix":
        return posix.checkupdates()

    raise NotImplementedError()


def get_preferred_application() -> posix.Application:
    """Return the preferred application."""

    if name == "posix":
        return posix.get_preferred_application()

    raise NotImplementedError()


def ping(host: str, count: int = 4) -> int:
    """Ping a host."""

    if name == "posix":
        return posix.ping(host, count=count)

    if name == "nt":
        return nt.ping(host, count=count)

    raise NotImplementedError()


def reboot(delay: int = 0) -> int:
    """Reboot the system."""

    if name == "posix":
        if delay:
            LOGGER.warning("Ignoring delay argument on POSIX system.")

        return posix.reboot()

    if name == "nt":
        return nt.reboot(delay=delay)

    raise NotImplementedError()


def screenshot() -> Screenshot:
    """Take a screenshot."""

    if name == "posix":
        return posix.screenshot()

    raise NotImplementedError()


def sensors() -> dict[str, Any]:
    """Return the system's temperature sensors and values."""

    if name == "posix":
        return posix.sensors()

    raise NotImplementedError()


def smartctl() -> dict:
    """Check SMART values of disks."""

    if name == "posix":
        return posix.device_states()

    raise NotImplementedError()


def sysinfo() -> dict:
    """Return miscellaneous system information."""

    if name != "posix":
        raise NotImplementedError()

    return posix.sysinfo()


def unlock_pacman() -> int:
    """Unlock the package manager."""

    if name == "posix":
        return posix.unlock_pacman()

    raise NotImplementedError()


def uptime() -> dict:
    """Return the system uptime."""

    if name == "posix":
        return posix.uptime()

    raise NotImplementedError()
