"""POSIX system commands."""

from digsigclt.rpc.posix.application import enable as enable_application
from digsigclt.rpc.posix.application import disable as disable_application
from digsigclt.rpc.posix.application import status as application_status
from digsigclt.rpc.posix.beep import beep
from digsigclt.rpc.posix.pacman import unlock as unlock_pacman
from digsigclt.rpc.posix.reboot import reboot
from digsigclt.rpc.posix.smartctl import device_states


__all__ = [
    'application_status',
    'beep',
    'device_states',
    'disable_application',
    'enable_application',
    'reboot',
    'unlock_pacman'
]
