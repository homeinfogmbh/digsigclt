"""Windows NT commands."""

from subprocess import check_call

from digsigclt.os.common import command


__all__ = ['beep', 'ping', 'reboot']


PING = 'C:\\Windows\\System32\\ping.exe'
REBOOT = 'C:\\Windows\\System32\\shutdown.exe'


def beep() -> int:
    """Performs a speaker beep to identify the system."""

    return check_call('@echo \x07', shell=True)


@command()
def ping(host: str, count: int = 4) -> list[str]:
    """Pings the system count times."""

    if count is None:
        return [PING, str(host), '/t']

    return [PING, str(host), '/n', str(count)]


@command()
def reboot(delay: int = 0) -> list[str]:
    """Reboots the system."""

    if delay is None:
        return [REBOOT, '/r']

    return [REBOOT, '/r', '/t', str(delay)]
