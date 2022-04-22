"""Application-related commands."""

from __future__ import annotations
from contextlib import suppress
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError

from digsigclt.os.common import command
from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.os.posix.pacman import pacman
from digsigclt.types import ApplicationVersion, ServiceState


__all__ = ['Application', 'enable', 'disable', 'status', 'version']


SERVICES_DIR = Path('/usr/lib/systemd/system')


class Application(ApplicationVersion, Enum):
    """Application types."""

    HTML = ApplicationVersion('html', 'html5ds.service')
    AIR = ApplicationVersion('air', 'application.service')

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

    for application in Application:
        if SERVICES_DIR.joinpath(application.service).is_file():
            return application

    raise ValueError('No service installed.')


def get_application(identifier: str | None = None) -> Application:
    """Returns the respective application type."""

    if identifier is None:
        return get_preferred_application()

    return Application.get(identifier)


@command()
def enable(identifier: str | None = None) -> list[str]:
    """Enables the digital signage application."""

    return sudo(
        systemctl('enable', '--now', get_application(identifier).service)
    )


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


def status() -> ServiceState:
    """Enables the digital signage application."""

    return ServiceState(
        {typ.name for typ in Application if is_enabled(typ)},
        {typ.name for typ in Application if is_running(typ)}
    )


def version(application: Application) -> str | None:
    """Returns the application version."""

    try:
        result = pacman('-Q', f'application-{application.name}')
    except CalledProcessError:
        return None

    _, version_ = result.stdout.strip().split()
    return version_
