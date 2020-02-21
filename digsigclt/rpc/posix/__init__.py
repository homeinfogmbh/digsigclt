"""POSIX system commands."""

from digsigclt.rpc.posix.application import enable as enable_application
from digsigclt.rpc.posix.application import disable as disable_application
from digsigclt.rpc.posix.application import status as application_status
from digsigclt.rpc.posix.beep import beep
from digsigclt.rpc.posix.pacman import unlock as unlock_pacman
from digsigclt.rpc.posix.reboot import reboot
from digsigclt.rpc.posix.smartctl import smartctl


__all__ = [
    'application_status',
    'beep',
    'disable_application',
    'enable_application',
    'reboot',
    'smartctl',
    'unlock_pacman'
]
