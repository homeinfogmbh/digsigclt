"""Application-related commands."""

from __future__ import annotations
from contextlib import suppress
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError
from typing import Iterator

from digsigclt.os.common import command, commands
from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.os.posix.pacman import pacman
from digsigclt.types import ApplicationVersion, Command, ServiceState


__all__ = ['Application', 'enable', 'disable', 'running', 'status', 'version']


APPLICATION_AIR = ApplicationVersion('air', 'application.service')
APPLICATION_HTML = ApplicationVersion('html', 'html5ds.service')
PRODUCTIVE_APPLICATIONS = (APPLICATION_AIR, APPLICATION_HTML)
SERVICES_DIR = Path('/usr/lib/systemd/system')


class Application(ApplicationVersion, Enum):
    """Application types."""

    HTML = APPLICATION_HTML
    AIR = APPLICATION_AIR
    NOT_CONFIGURED = ApplicationVersion(
        'not configured',
        'unconfigured-warning.service'
    )
    INSTALLATION_INSTRUCTIONS = ApplicationVersion(
        'html',
        'installation-instructions.service'
    )

    @classmethod
    def get(cls, identifier: str) -> Application:
        """Returns the respective Application type."""
        with suppress(ValueError):
            return cls(identifier)

        with suppress(KeyError):
            return cls[identifier]

        for typ in cls:
            if typ.name == identifier or typ.service == identifier:
                return typ

        raise ValueError('Invalid service.')


def get_preferred_application() -> Application:
    """Returns the preferred service on the system."""

    for application_version in PRODUCTIVE_APPLICATIONS:
        if SERVICES_DIR.joinpath(application_version.service).is_file():
            return Application(application_version)

    raise ValueError('No productive application installed.')


def get_application(identifier: str | None = None) -> Application:
    """Returns the respective application type."""

    if identifier is None:
        return get_preferred_application()

    return Application.get(identifier)


@commands()
def enable(identifier: str | None = None) -> Iterator[list[str]]:
    """Enables the digital signage application."""

    to_be_enabled = get_application(identifier)

    for application in Application:
        if application is not to_be_enabled:
            yield Command(
                sudo(systemctl('disable', '--now', application.service)),
                exit_ok={1}
            )

    yield Command(sudo(systemctl('enable', '--now', to_be_enabled.service)))


@command()
def disable(identifier: str | None = None) -> list[str]:
    """Disables the digital signage application."""

    return sudo(
        systemctl('disable', '--now', get_application(identifier).service)
    )


@command(as_bool=True)
def is_enabled(application: Application) -> list[str]:
    """Checks whether the respective service is enabled."""

    return systemctl('is-enabled', application.service)


@command(as_bool=True)
def is_running(application: Application) -> list[str]:
    """Checks whether the respective service is running."""

    return systemctl('is-active', application.service)


def running() -> Application | None:
    """Returns the currently running application type."""

    for application in Application:
        if is_running(application):
            return application

    return None


def status() -> ServiceState:
    """Enables the digital signage application."""

    return ServiceState(
        {typ.name for typ in Application if is_running(typ)},
        {typ.name for typ in Application if is_enabled(typ)}
    )


def version(application: Application | None) -> str | None:
    """Returns the application version."""

    if application is None:
        return None

    try:
        result = pacman('-Q', f'application-{application.name}')
    except CalledProcessError:
        return None

    _, version_ = result.stdout.strip().split()
    return version_
