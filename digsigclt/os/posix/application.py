"""Application-related commands."""

from __future__ import annotations
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError, check_call

from digsigclt.os.common import commands
from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.os.posix.pacman import package_version
from digsigclt.types import Command, ServiceState


__all__ = ['set_mode', 'status', 'versions']


SERVICES_DIR = Path('/usr/lib/systemd/system')
PRODUCTIVE_APPLICATIONS = ('html5ds.service', 'application.service')
NOT_CONFIGURED_WARNING = 'unconfigured-warning.service'
INSTALLATION_INSTRUCTIONS = 'installation-instructions.service'
UNITS = {
    *PRODUCTIVE_APPLICATIONS,
    NOT_CONFIGURED_WARNING,
    INSTALLATION_INSTRUCTIONS
}
PACKAGES = {
    'application-air',
    'application-html',
    'html5ds',
    'chromium'
}


class Mode(str, Enum):
    """Application modes."""

    PRODUCTIVE = 'productive'
    INSTALLATION_INSTRUCTIONS = 'installation instructions'
    NOT_CONFIGURED = 'not configured'
    OFF = 'off'


def get_preferred_application() -> str:
    """Return the preferred service on the system."""

    for unit in PRODUCTIVE_APPLICATIONS:
        if SERVICES_DIR.joinpath(unit).is_file():
            return unit

    raise ValueError('No productive application installed.')


def get_application(mode: Mode) -> str | None:
    """Return the respective application type."""

    if mode is Mode.PRODUCTIVE:
        return get_preferred_application()

    if mode is Mode.INSTALLATION_INSTRUCTIONS:
        return INSTALLATION_INSTRUCTIONS

    if mode is Mode.NOT_CONFIGURED:
        return NOT_CONFIGURED_WARNING

    if mode is Mode.OFF:
        return None

    raise ValueError('Invalid mode:', mode)


@commands()
def set_mode(mode: str) -> int:
    """Set application mode."""

    for unit in UNITS:
        yield Command(sudo(systemctl('disable', '--now', unit)), exit_ok={1})

    if unit := get_application(Mode[mode.upper()]):
        yield Command(sudo(systemctl('enable', '--now', unit)))


def status() -> ServiceState:
    """Return unit statuses."""

    return ServiceState(
        set(filter(is_running, UNITS)),
        set(filter(is_enabled, UNITS))
    )


def versions() -> dict[str, str | None]:
    """Return the package versions."""

    return {package: package_version(package) for package in PACKAGES}


def is_enabled(unit: str) -> bool:
    """Check whether the unit is enabled."""

    try:
        check_call(systemctl('is-enabled', unit))
    except CalledProcessError:
        return False

    return True


def is_running(unit: str) -> bool:
    """Check whether the unit is running."""

    try:
        check_call(systemctl('is-running', unit))
    except CalledProcessError:
        return False

    return True
