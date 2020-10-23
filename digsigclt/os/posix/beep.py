"""System identification via beep."""

from subprocess import check_call


__all__ = ['beep']


BEEP = '/usr/bin/beep'


def beep(args: tuple = ()) -> int:
    """Performs a speaker beep to identify the system."""

    command = (BEEP, *args) if args else BEEP
    return check_call(command)
