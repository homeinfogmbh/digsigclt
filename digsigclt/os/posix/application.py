"""Application-related commands."""

from pathlib import Path
from typing import Optional

from digsigclt.os.common import command
from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.types import ServiceState


__all__ = ['enable', 'disable', 'get_service', 'status']


SERVICES_DIR = Path('/usr/lib/systemd/system')
SERVICE_AIR = 'application.service'
SERVICE_HTML = 'html5ds.service'
SERVICES = {SERVICE_AIR, SERVICE_HTML}


def get_preferred_service() -> str:
    """Returns the preferred service on the system."""

    for service in [SERVICE_HTML, SERVICE_AIR]:
        if SERVICES_DIR.joinpath(service).is_file():
            return service

    raise ValueError('No service installed.')


def get_service(service: Optional[str] = None) -> str:
    """Returns the respective service."""

    if service is None:
        return get_preferred_service()

    if service not in SERVICES:
        raise ValueError('Invalid service.')

    return service


@command()
def enable(service: Optional[str] = None) -> list[str]:
    """Enables the digital signage application."""

    return sudo(systemctl('enable', '--now', get_service(service)))


@command()
def disable(service: Optional[str] = None) -> list[str]:
    """Disables the digital signage application."""

    return sudo(systemctl('disable', '--now', get_service(service)))


@command(as_bool=True)
def is_enabled(service: str) -> list[str]:
    """Checks whether the respective service is enabled."""

    return systemctl('is-enabled', service)


@command(as_bool=True)
def is_running(service: str) -> list[str]:
    """Checks whether the respective service is running."""

    return systemctl('is-active', service)


def status() -> ServiceState:
    """Enables the digital signage application."""

    enabled = {service for service in SERVICES if is_enabled(service)}
    running = {service for service in SERVICES if is_running(service)}
    return ServiceState(enabled, running)
