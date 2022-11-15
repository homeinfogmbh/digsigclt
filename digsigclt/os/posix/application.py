"""Application-related commands."""

from __future__ import annotations
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError, check_call

from digsigclt.os.common import commands
from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.os.posix.pacman import package_version
from digsigclt.types import Application, ApplicationMode, Command


__all__ = ['Applications', 'set_mode', 'status', 'versions']


SERVICES_DIR = Path('/usr/lib/systemd/system')
PACKAGES = {
    'application-air',
    'application-html',
    'html5ds',
    'chromium'
}


class Applications(Application, Enum):
    """Available applications."""

    HTML = Application('html', ApplicationMode.PRODUCTIVE, 'html5ds.service')
    AIR = Application(
        'html',
        ApplicationMode.PRODUCTIVE,
        'application.service'
    )
    NOT_CONFIGURED_WARNING = Application(
        'not configured',
        ApplicationMode.NOT_CONFIGURED,
        'unconfigured-warning.service'
    )
    INSTALLATION_INSTRUCTIONS = Application(
        'installation instructions',
        ApplicationMode.INSTALLATION_INSTRUCTIONS,
        'installation-instructions.service'
    )
    NONE = Application(
        'none',
        ApplicationMode.OFF,
        None
    )


def get_preferred_application() -> Applications:
    """Return the preferred service on the system."""

    for application in Applications:
        if application.unit and application.mode == ApplicationMode.PRODUCTIVE:
            if SERVICES_DIR.joinpath(application.unit).is_file():
                return application

    raise ValueError('No productive application installed.')


def get_application(mode: ApplicationMode) -> Application:
    """Return the respective application type."""

    if mode is ApplicationMode.PRODUCTIVE:
        return get_preferred_application()

    if mode is ApplicationMode.INSTALLATION_INSTRUCTIONS:
        return Applications.INSTALLATION_INSTRUCTIONS

    if mode is ApplicationMode.NOT_CONFIGURED:
        return Applications.NOT_CONFIGURED_WARNING

    if mode is ApplicationMode.OFF:
        return Applications.NONE

    raise ValueError('Invalid mode:', mode)


@commands()
def set_mode(mode: str) -> int:
    """Set application mode."""

    for application in Applications:
        yield Command(
            sudo(
                systemctl('disable', '--now', application.unit)
            ),
            exit_ok={1}
        )

    if unit := get_application(ApplicationMode[mode.upper()]).unit:
        yield Command(sudo(systemctl('enable', '--now', unit)))


def status() -> Applications:
    """Return the current mode."""

    for application in Applications:
        if application.unit:
            if is_enabled(application.unit) and is_running(application.unit):
                return application

    return Applications.NONE


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
