"""Application-related commands."""

from subprocess import CalledProcessError, check_call

from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.types import ServiceState


__all__ = ['enable', 'disable', 'status']


SERVICE_AIR = 'application.service'
SERVICE_HTML = 'html5ds.service'
SERVICES = {SERVICE_AIR, SERVICE_HTML}


def enable(service: str) -> int:
    """Enables the digital signage application."""

    if service not in SERVICES:
        raise ValueError('Invalid service.')

    return check_call(sudo(systemctl('enable', '--now', service)))


def disable(service: str) -> int:
    """Disables the digital signage application."""

    if service not in SERVICES:
        raise ValueError('Invalid service.')

    return check_call(sudo(systemctl('disable', '--now', service)))


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
