"""Application-related commands."""

from subprocess import CalledProcessError, check_call

from digsigclt.os.posix.common import sudo, systemctl
from digsigclt.types import ServiceState


__all__ = ['enable', 'disable', 'status']


SERVICE = 'application.service'
ENABLE = sudo(systemctl('enable', '--now', SERVICE))
DISABLE = sudo(systemctl('disable', '--now', SERVICE))
CHECK_ENABLED = systemctl('is-enabled', SERVICE)
CHECK_RUNNING = systemctl('is-active', SERVICE)


def enable() -> int:
    """Enables the digital signage application."""

    return check_call(ENABLE)


def disable() -> int:
    """Disables the digital signage application."""

    return check_call(DISABLE)


def status() -> ServiceState:
    """Enables the digital signage application."""

    try:
        check_call(CHECK_ENABLED)
    except CalledProcessError:
        enabled = False
    else:
        enabled = True

    try:
        check_call(CHECK_RUNNING)
    except CalledProcessError:
        running = False
    else:
        running = True

    return ServiceState(enabled, running)
