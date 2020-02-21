"""Application-related commands."""

from subprocess import CalledProcessError, check_call

from digsigclt.common import ServiceState
from digsigclt.rpc.posix.common import sudo, systemctl


__all__ = ['enable', 'disable', 'status']


SERVICE = 'application.service'
ENABLE = sudo(systemctl('enable', '--now', SERVICE))
DISABLE = sudo(systemctl('disable', '--now', SERVICE))
CHECK_ENABLED = systemctl('is-enabled', SERVICE)
CHECK_RUNNING = systemctl('is-active', SERVICE)


def enable():
    """Enables the digital signage application."""

    return check_call(ENABLE)


def disable():
    """Disables the digital signage application."""

    return check_call(DISABLE)


def status():
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
