"""Windows NT commands."""

from subprocess import check_call


__all__ = ['beep', 'ping', 'reboot']


PING = 'C:\\Windows\\System32\\ping.exe'
REBOOT = 'C:\\Windows\\System32\\shutdown.exe'


def beep() -> int:
    """Performs a speaker beep to identify the system."""

    return check_call('@echo \x07', shell=True)


def ping(host: str, count: int = 4) -> int:
    """Pings the system count times."""

    if count is None:
        command = (PING, str(host), '/t')
    else:
        command = (PING, str(host), '/n', str(count))

    return check_call(command)


def reboot(delay: int = 0) -> int:
    """Reboots the system."""

    if delay is None:
        command = (REBOOT, '/r')
    else:
        command = (REBOOT, '/r', '/t', str(delay))

    return check_call(command)
