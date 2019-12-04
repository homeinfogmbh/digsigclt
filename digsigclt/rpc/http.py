"""Wrapper functions to run commands from HTTP requests."""

from digsigclt.rpc import os
from digsigclt.rpc.util import ExceptionHandler


__all__ = ['COMMANDS']


def beep(args=None):
    """Runs the beep function, handles exceptions
    and returns a JSON response and a HTTP status code.
    """

    with ExceptionHandler('System should have beeped.') as handler:
        os.beep(args=args)

    return handler


def reboot(delay=0):
    """Runs a reboot."""

    with ExceptionHandler('System is rebooting.') as handler:
        os.reboot(delay=delay)

    return handler


def unlock_pacman():
    """Removes the pacman lockfile."""

    with ExceptionHandler('Lockfile removed.') as handler:
        os.unlock_pacman()

    return handler


def application(state):
    """Handles the application state."""

    if state is None:
        with ExceptionHandler(None) as handler:
            state = os.application_status()
            json = {'enabled': state.enabled, 'running': state.running}
            return (json, 200)

        return handler

    if state:
        function = os.enable_application
        text = 'Application enabled.'
    else:
        function = os.disable_application
        text = 'Application disabled.'

    with ExceptionHandler(text) as handler:
        function()

    return handler


COMMANDS = {
    'beep': beep,
    'reboot': reboot,
    'unlock-pacman': unlock_pacman,
    'application': application
}
