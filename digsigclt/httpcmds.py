"""Wrapper functions to run commands from HTTP requests."""

from subprocess import CalledProcessError

from digsigclt.commands import beep
from digsigclt.commands import reboot
from digsigclt.commands import unlock_pacman
from digsigclt.commands import enable_application
from digsigclt.commands import disable_application
from digsigclt.commands import application_status
from digsigclt.exceptions import UnderAdministration, PackageManagerActive


__all__ = ['COMMANDS']


class ExceptionHandler:
    """Handles common exceptions."""

    def __init__(self, text, status_code=200):
        """Sets initial text and status code."""
        self.text = text
        self.status_code = status_code

    def __enter__(self):
        """Enters a context and returns itself."""
        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        if typ is NotImplementedError:
            self.text = 'Beeping is not implemented on this platform.'
            self.status_code = 501
        elif typ is CalledProcessError:
            self.text = str(value)
            self.status_code = 500
        elif typ is UnderAdministration:
            self.text = 'The system is currently under administration.'
            self.status_code = 503
        elif typ is PackageManagerActive:
            self.text = 'The package manager is currently running.'
            self.status_code = 503
        else:
            return False

        return True

    def __iter__(self):
        """Returns the text and status code."""
        yield self.text
        yield self.status_code


def do_beep(args=None):
    """Runs the beep function, handles exceptions
    and returns a JSON response and a HTTP status code.
    """

    with ExceptionHandler('System should have beeped.') as handler:
        beep(args=args)

    return handler


def do_reboot(delay=0):
    """Runs a reboot."""

    with ExceptionHandler('System is rebooting.') as handler:
        reboot(delay=delay)

    return handler


def do_unlock_pacman():
    """Removes the pacman lockfile."""

    with ExceptionHandler('Lockfile removed.') as handler:
        unlock_pacman()

    return handler


def handle_application(state):
    """Handles the application state."""

    if state is None:
        with ExceptionHandler(None) as handler:
            state = application_status()
            json = {'enabled': state.enabled, 'running': state.running}
            return (json, 200)

        return handler

    if state:
        function = enable_application
        text = 'Application enabled.'
    else:
        function = disable_application
        text = 'Application disabled.'

    with ExceptionHandler(text) as handler:
        function()

    return handler


COMMANDS = {
    'beep': do_beep,
    'reboot': do_reboot,
    'unlock-pacman': do_unlock_pacman,
    'application': handle_application
}
