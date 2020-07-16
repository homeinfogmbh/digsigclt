"""POSIX system commands."""

from digsigclt.os.posix.application import enable as enable_application
from digsigclt.os.posix.application import disable as disable_application
from digsigclt.os.posix.application import status as application_status
from digsigclt.os.posix.beep import beep
from digsigclt.os.posix.pacman import unlock as unlock_pacman
from digsigclt.os.posix.ping import ping
from digsigclt.os.posix.reboot import reboot
from digsigclt.os.posix.smartctl import device_states
from digsigclt.os.posix.uptime import uptime


__all__ = [
    'application_status',
    'beep',
    'device_states',
    'disable_application',
    'enable_application',
    'ping',
    'reboot',
    'unlock_pacman',
    'uptime'
]
