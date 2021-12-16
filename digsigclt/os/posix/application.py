"""Application-related commands."""

from pathlib import Path
from subprocess import CalledProcessError, check_call
from typing import Optional

from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.types import ServiceState


__all__ = ['enable', 'disable', 'status']


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


def get_service(service: Optional[str]) -> str:
    """Returns the respective service."""

    if service is None:
        return get_preferred_service()

    if service not in SERVICES:
        raise ValueError('Invalid service.')

    return service


def enable(service: Optional[str] = None) -> int:
    """Enables the digital signage application."""

    return check_call(sudo(systemctl('enable', '--now', get_service(service))))


def disable(service: Optional[str] = None) -> int:
    """Disables the digital signage application."""

    return check_call(
        sudo(systemctl('disable', '--now', get_service(service)))
    )


def is_enabled(service: str) -> bool:
    """Checks whether the respective service is enabled."""

    try:
        check_call(systemctl('is-enabled', service))
    except CalledProcessError:
        return  False

    return True


def is_running(service: str) -> bool:
    """Checks whether the respective service is running."""

    try:
        check_call(systemctl('is-active', service))
    except CalledProcessError:
        return False

    return True


def status() -> ServiceState:
    """Enables the digital signage application."""

    enabled = {service for service in SERVICES if is_enabled(service)}
    running = {service for service in SERVICES if is_running(service)}
    return ServiceState(enabled, running)
