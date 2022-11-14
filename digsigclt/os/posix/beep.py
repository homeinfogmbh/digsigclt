"""System identification via beep."""

from digsigclt.os.common import command


__all__ = ['beep']


BEEP = '/usr/bin/beep'


@command()
def beep(args: tuple = ()) -> list[str]:
    """Perform a speaker beep to identify the system."""

    return [BEEP, *args]
