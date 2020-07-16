"""Wrapper functions to run commands from HTTP requests."""

from digsigclt.os import application_status
from digsigclt.os import beep
from digsigclt.os import disable_application
from digsigclt.os import enable_application
from digsigclt.os import reboot
from digsigclt.os import smartctl
from digsigclt.os import unlock_pacman
from digsigclt.rpc.util import JSONResponse


__all__ = ['COMMANDS']


def http_beep(args=None):
    """Runs the beep function, handles exceptions
    and returns a JSON response and a HTTP status code.
    """

    with JSONResponse('System should have beeped.') as handler:
        beep(args=args)

    return handler


def http_reboot(delay=0):
    """Runs a reboot."""

    with JSONResponse('System is rebooting.') as handler:
        reboot(delay=delay)

    return handler


def http_unlock_pacman():
    """Removes the pacman lockfile."""

    with JSONResponse('Lockfile removed.') as handler:
        unlock_pacman()

    return handler


def http_application(state=None):
    """Handles the application state."""

    if state is None:
        with JSONResponse() as handler:
            state = application_status()
            handler.json = state.to_json()

        return handler

    if state:
        function = enable_application
        text = 'Application enabled.'
    else:
        function = disable_application
        text = 'Application disabled.'

    with JSONResponse(text) as handler:
        function()

    return handler


def http_smartctl():
    """Checks the SMART values of the disks."""

    with JSONResponse() as handler:
        handler.json = smartctl()

    return handler


COMMANDS = {
    'beep': http_beep,
    'reboot': http_reboot,
    'unlock-pacman': http_unlock_pacman,
    'application': http_application,
    'smartctl': http_smartctl
}
