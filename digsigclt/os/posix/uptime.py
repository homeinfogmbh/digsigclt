"""Returns the uptime."""

from subprocess import check_output


__all__ = ['uptime']


UPTIME = '/usr/bin/uptime'


def uptime() -> str:
    """Returns the system uptime."""

    return check_output(UPTIME, text=True)
