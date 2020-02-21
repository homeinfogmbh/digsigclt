"""System identification via beep."""

from subprocess import check_call


__all__ = ['beep']


def beep(args=None):
    """Performs a speaker beep to identify the system."""

    command = ['/usr/bin/beep']

    if args:
        command += args

    return check_call(command)
