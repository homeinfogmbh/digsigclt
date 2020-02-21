"""System identification via beep."""

from subprocess import check_call


__all__ = ['beep']


BEEP = '/usr/bin/beep'


def beep(args=None):
    """Performs a speaker beep to identify the system."""

    if args:
        command = (BEEP,) + tuple(args)
    else:
        command = BEEP

    return check_call(command)
