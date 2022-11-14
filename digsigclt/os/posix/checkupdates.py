"""Check for available updates."""

from os import linesep
from subprocess import CalledProcessError, check_output


__all__ = ['checkupdates']


CHECKUPDATES = '/usr/bin/checkupdates'


def checkupdates() -> dict:
    """Return package updates in a JSON-ish dict."""

    json = {}

    try:
        text = check_output(CHECKUPDATES, text=True)
    except CalledProcessError as error:
        if error.returncode == 2:
            return json

        raise

    for line in filter(None, text.split(linesep)):
        package, old_version, _, new_version = line.split()
        json[package] = (old_version, new_version)

    return json
