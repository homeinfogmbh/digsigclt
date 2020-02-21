"""Wrapper functions to run commands from HTTP requests."""

from digsigclt.rpc import os
from digsigclt.rpc.util import JSONResponse


__all__ = ['COMMANDS']


def beep(args=None):
    """Runs the beep function, handles exceptions
    and returns a JSON response and a HTTP status code.
    """

    with JSONResponse('System should have beeped.') as handler:
        os.beep(args=args)

    return handler


def reboot(delay=0):
    """Runs a reboot."""

    with JSONResponse('System is rebooting.') as handler:
        os.reboot(delay=delay)

    return handler


def unlock_pacman():
    """Removes the pacman lockfile."""

    with JSONResponse('Lockfile removed.') as handler:
        os.unlock_pacman()

    return handler


def application(state=None):
    """Handles the application state."""

    if state is None:
        with JSONResponse() as handler:
            state = os.application_status()
            handler.json = state.to_json()

        return handler

    if state:
        function = os.enable_application
        text = 'Application enabled.'
    else:
        function = os.disable_application
        text = 'Application disabled.'

    with JSONResponse(text) as handler:
        function()

    return handler


def smartctl():
    """Checks the SMART values of the disks."""

    with JSONResponse() as handler:
        handler.json = os.smartctl()

    return handler


COMMANDS = {
    'beep': beep,
    'reboot': reboot,
    'unlock-pacman': unlock_pacman,
    'application': application,
    'smartctl': smartctl
}
