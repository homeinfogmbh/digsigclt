"""Implementation of ping command."""

from digsigclt.os.common import command


__all__ = ['ping']


PING = '/usr/bin/ping'


@command()
def ping(host: str, count: int = 4, quiet: bool = True) -> list[str]:
    """Ping a host."""

    if count is None:
        return [PING, str(host)] + ['-q'] * quiet

    return [PING, str(host), '-c', str(count)] + ['-q'] * quiet
