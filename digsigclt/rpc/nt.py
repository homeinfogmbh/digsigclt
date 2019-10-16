"""Windows NT commands."""

from subprocess import check_call


__all__ = ['beep', 'reboot']


REBOOT = ('C:\\Windows\\System32\\shutdown.exe', '/r')


def beep():
    """Performs a speaker beep to identify the system."""

    return check_call('@echo \x07', shell=True)


def reboot(delay=0):
    """Reboots the system."""

    command = REBOOT

    if delay is not None:
        command += ('/t', str(delay))

    return check_call(command)
