"""Application-related commands."""

from subprocess import CalledProcessError, check_call
from typing import Optional

from digsigclt.os.posix.common import sudo, systemctl, list_journal
from digsigclt.types import ServiceState


__all__ = ['enable', 'disable', 'status', 'get_log']


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


def get_log(boot: Optional[int] = None) -> dict:
    """Returns the journal for the application."""

    return list_journal(get_service(), boot)
