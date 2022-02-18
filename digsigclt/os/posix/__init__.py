"""POSIX system commands."""

from digsigclt.os.posix.application import enable as enable_application
from digsigclt.os.posix.application import disable as disable_application
from digsigclt.os.posix.application import get_service
from digsigclt.os.posix.application import status as application_status
from digsigclt.os.posix.beep import beep
from digsigclt.os.posix.checkupdates import checkupdates
from digsigclt.os.posix.cmdline import cmdline
from digsigclt.os.posix.common import list_journal
from digsigclt.os.posix.cpuinfo import cpuinfo, is_baytrail
from digsigclt.os.posix.meminfo import meminfo
from digsigclt.os.posix.pacman import unlock as unlock_pacman
from digsigclt.os.posix.ping import ping
from digsigclt.os.posix.reboot import reboot
from digsigclt.os.posix.screenshot import screenshot
from digsigclt.os.posix.smartctl import device_states
from digsigclt.os.posix.uptime import uptime


__all__ = [
    'application_status',
    'beep',
    'checkupdates',
    'cmdline',
    'cpuinfo',
    'device_states',
    'disable_application',
    'enable_application',
    'get_service',
    'is_baytrail',
    'list_journal',
    'meminfo',
    'ping',
    'reboot',
    'screenshot',
    'unlock_pacman',
    'uptime'
]
