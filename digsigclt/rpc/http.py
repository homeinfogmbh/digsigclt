"""Wrapper functions to run commands from HTTP requests."""

from typing import Optional

from digsigclt.os import application_status
from digsigclt.os import beep
from digsigclt.os import checkupdates
from digsigclt.os import disable_application
from digsigclt.os import enable_application
from digsigclt.os import reboot
from digsigclt.os import screenshot
from digsigclt.os import smartctl
from digsigclt.os import unlock_pacman
from digsigclt.rpc.response import Response


__all__ = ['COMMANDS']


def http_application(state: Optional[bool] = None) -> Response:
    """Handles the application state."""

    if state is None:
        with Response() as response:
            state = application_status()
            response.payload = state.to_json()

        return response

    if state:
        function = enable_application
        text = 'Application enabled.'
    else:
        function = disable_application
        text = 'Application disabled.'

    with Response(text) as response:
        function()

    return response


def http_beep(args: tuple = ()) -> Response:
    """Runs the beep function, handles exceptions
    and returns a JSON response and a HTTP status code.
    """

    with Response('System should have beeped.') as response:
        beep(args=args)

    return response


def http_checkupdates() -> Response:
    """Checks the SMART values of the disks."""

    with Response() as response:
        response.payload = checkupdates()

    return response


def http_reboot(delay: int = 0) -> Response:
    """Runs a reboot."""

    with Response('System is rebooting.') as response:
        reboot(delay=delay)

    return response


def http_screenshot() -> Response:
    """Returns a screenshot or an error message."""

    with Response() as response:
        response.payload, response.content_type = screenshot()

    return response


def http_smartctl() -> Response:
    """Checks the SMART values of the disks."""

    with Response() as response:
        response.payload = smartctl()

    return response


def http_unlock_pacman() -> Response:
    """Removes the pacman lockfile."""

    with Response('Lockfile removed.') as response:
        unlock_pacman()

    return response


COMMANDS = {
    'application': http_application,
    'beep': http_beep,
    'checkupdates': http_checkupdates,
    'reboot': http_reboot,
    'screenshot': http_screenshot,
    'smartctl': http_smartctl,
    'unlock-pacman': http_unlock_pacman
}
