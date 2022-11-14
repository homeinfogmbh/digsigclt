"""Application-related commands."""

from __future__ import annotations
from pathlib import Path
from subprocess import CalledProcessError, check_call

from digsigclt.os.common import commands
from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.os.posix.pacman import package_version
from digsigclt.types import ApplicationMode, Command


__all__ = ['set_mode', 'status', 'versions']


SERVICES_DIR = Path('/usr/lib/systemd/system')
PRODUCTIVE_APPLICATIONS = ('html5ds.service', 'application.service')
NOT_CONFIGURED_WARNING = 'unconfigured-warning.service'
INSTALLATION_INSTRUCTIONS = 'installation-instructions.service'
UNITS = {
    **{
        unit: ApplicationMode.PRODUCTIVE for unit in PRODUCTIVE_APPLICATIONS
    },
    NOT_CONFIGURED_WARNING: ApplicationMode.NOT_CONFIGURED,
    INSTALLATION_INSTRUCTIONS: ApplicationMode.NOT_CONFIGURED
}
PACKAGES = {
    'application-air',
    'application-html',
    'html5ds',
    'chromium'
}


def get_preferred_application() -> str:
    """Return the preferred service on the system."""

    for unit in PRODUCTIVE_APPLICATIONS:
        if SERVICES_DIR.joinpath(unit).is_file():
            return unit

    raise ValueError('No productive application installed.')


def get_application(mode: ApplicationMode) -> str | None:
    """Return the respective application type."""

    if mode is ApplicationMode.PRODUCTIVE:
        return get_preferred_application()

    if mode is ApplicationMode.INSTALLATION_INSTRUCTIONS:
        return INSTALLATION_INSTRUCTIONS

    if mode is ApplicationMode.NOT_CONFIGURED:
        return NOT_CONFIGURED_WARNING

    if mode is ApplicationMode.OFF:
        return None

    raise ValueError('Invalid mode:', mode)


@commands()
def set_mode(mode: str) -> int:
    """Set application mode."""

    for unit in UNITS:
        yield Command(sudo(systemctl('disable', '--now', unit)), exit_ok={1})

    if unit := get_application(ApplicationMode[mode.upper()]):
        yield Command(sudo(systemctl('enable', '--now', unit)))


def status() -> ApplicationMode:
    """Return the current mode."""

    for unit, mode in UNITS.items():
        if is_enabled(unit) and is_running(unit):
            return mode

    return ApplicationMode.OFF


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
