"""Implementation of ping command."""

from subprocess import check_call


__all__ = ['ping']


PING = '/usr/bin/ping'


def ping(host, count=4):
    """Pings a host."""

    if count is None:
        command = (PING, str(host))
    else:
        command = (PING, str(host), '-c', str(count))

    return check_call(command)
