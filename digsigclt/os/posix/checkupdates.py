"""Check for available updates."""

from os import linesep
from subprocess import check_output


CHECKUPDATES = '/usr/bin/checkupdates'


def checkupdates():
    """Returns package updates in a JSON-ish dict."""

    try:
        text = check_output(CHECKUPDATES, text=True)
    except FileNotFoundError:
        return None

    result = {}

    for line in filter(None, text.split(linesep)):
        package, old_version, _, new_version = line.split()
        result[package] = (old_version, new_version)

    return result
