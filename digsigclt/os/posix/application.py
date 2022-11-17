"""Application-related commands."""

from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from digsigclt.os.common import commands
from digsigclt.os.posix.common import sudo, systemctl, is_active, is_enabled
from digsigclt.os.posix.pacman import package_version
from digsigclt.types import ApplicationMode, Command


__all__ = ['Application', 'set_mode', 'status']


SERVICES_DIR = Path('/usr/lib/systemd/system')


class Application(NamedTuple):
    """Application types."""

    name: str
    mode: ApplicationMode
    unit: str | None = None
    package: str | None = None

    @property
    def version(self) -> str | None:
        """Return the package version."""
        if package := self.package:
            return package_version(package)

        return None

    def to_json(self) -> dict[str, str]:
        """Return a JSON-ish dict."""
        return {
            'name': self.name,
            'mode': self.mode.name,
            'unit': self.unit,
            'package': self.package,
            'version': self.version
        }


class Applications(Application, Enum):
    """Available applications."""

    HTML = Application(
        'html',
        ApplicationMode.PRODUCTIVE,
        'html5ds.service',
        'application-html'
    )
    AIR = Application(
        'air',
        ApplicationMode.PRODUCTIVE,
        'application.service',
        'application-air'
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
    OFF = Application('off', ApplicationMode.OFF)


def get_preferred_application() -> Application:
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
        return Applications.OFF

    raise ValueError('Invalid mode:', mode)


@commands()
def set_mode(mode: str) -> int:
    """Set application mode."""

    for application in Applications:
        if unit := application.unit:
            yield Command(
                sudo(systemctl('disable', '--now', unit)),
                exit_ok={1}
            )

    if unit := get_application(ApplicationMode[mode.upper()]).unit:
        yield Command(sudo(systemctl('enable', '--now', unit)))


def status() -> Application:
    """Return the current mode."""

    for application in Applications:
        if (
                application.unit
                and is_enabled(application.unit)
                and is_active(application.unit)
        ):
            return application

    return Applications.OFF
