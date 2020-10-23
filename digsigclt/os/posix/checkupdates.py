"""Check for available updates."""

from os import linesep
from subprocess import check_output


__all__ = ['checkupdates']


CHECKUPDATES = '/usr/bin/checkupdates'


def checkupdates() -> dict:
    """Returns package updates in a JSON-ish dict."""

    json = {}
    text = check_output(CHECKUPDATES, text=True)

    for line in filter(None, text.split(linesep)):
        package, old_version, _, new_version = line.split()
        json[package] = (old_version, new_version)

    return json
