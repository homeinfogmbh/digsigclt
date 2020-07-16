"""Windows NT commands."""

from subprocess import check_call


__all__ = ['beep', 'ping', 'reboot']


PING = 'C:\\Windows\\System32\\ping.exe'
REBOOT = ('C:\\Windows\\System32\\shutdown.exe', '/r')


def beep():
    """Performs a speaker beep to identify the system."""

    return check_call('@echo \x07', shell=True)


def ping(host, count=4):
    """Pings the system count times."""

    if count is None:
        command = (PING, str(host), '/t')
    else:
        command = (PING, str(host), '/n', str(count))

    return check_call(command)


def reboot(delay=0):
    """Reboots the system."""

    command = REBOOT

    if delay is not None:
        command += ('/t', str(delay))

    return check_call(command)
