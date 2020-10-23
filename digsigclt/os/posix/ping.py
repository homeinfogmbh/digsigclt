"""Implementation of ping command."""

from subprocess import check_call


__all__ = ['ping']


PING = '/usr/bin/ping'


def ping(host: str, count: int = 4, quiet: bool = True) -> int:
    """Pings a host."""

    if count is None:
        command = [PING, str(host)]
    else:
        command = [PING, str(host), '-c', str(count)]

    if quiet:
        command.append('-q')

    return check_call(command)
