"""Application-related commands."""

from subprocess import CalledProcessError, check_call

from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.types import ServiceState


__all__ = ['SERVICE_AIR', 'SERVICE_HTML', 'enable', 'disable', 'status']


SERVICE_AIR = 'application.service'
SERVICE_HTML = 'html5ds.service'


def get_service() -> str:
    """Returns the service."""

    try:
        check_call(systemctl('status', SERVICE_HTML))
    except CalledProcessError as cpe:
        if cpe.returncode == 4:     # HTML version not installed.
            return SERVICE_AIR

    return SERVICE_HTML


def enable() -> int:
    """Enables the digital signage application."""

    return check_call(sudo(systemctl('enable', '--now', get_service())))


def disable() -> int:
    """Disables the digital signage application."""

    return check_call(sudo(systemctl('disable', '--now', get_service())))


def status() -> ServiceState:
    """Enables the digital signage application."""

    service = get_service()

    try:
        check_call(systemctl('is-enabled', service))
    except CalledProcessError:
        enabled = False
    else:
        enabled = True

    try:
        check_call(systemctl('is-active', service))
    except CalledProcessError:
        running = False
    else:
        running = True

    return ServiceState(enabled, running)
