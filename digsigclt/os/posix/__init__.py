"""POSIX system commands."""

from digsigclt.os.posix.application import Application
from digsigclt.os.posix.application import set_mode as application_set_mode
from digsigclt.os.posix.application import status as application_status
from digsigclt.os.posix.beep import beep
from digsigclt.os.posix.checkupdates import checkupdates
from digsigclt.os.posix.cmdline import cmdline
from digsigclt.os.posix.common import list_journal
from digsigclt.os.posix.cpuinfo import cpuinfo, is_baytrail
from digsigclt.os.posix.meminfo import meminfo
from digsigclt.os.posix.mount import efi_mounted_as_boot, root_mounted_ro
from digsigclt.os.posix.pacman import unlock as unlock_pacman
from digsigclt.os.posix.ping import ping
from digsigclt.os.posix.reboot import reboot
from digsigclt.os.posix.screenshot import screenshot
from digsigclt.os.posix.sensors import sensors
from digsigclt.os.posix.smartctl import device_states
from digsigclt.os.posix.sysinfo import sysinfo
from digsigclt.os.posix.uptime import uptime


__all__ = [
    'Application',
    'application_set_mode',
    'application_status',
    'beep',
    'checkupdates',
    'cmdline',
    'cpuinfo',
    'device_states',
    'efi_mounted_as_boot',
    'is_baytrail',
    'list_journal',
    'meminfo',
    'ping',
    'reboot',
    'root_mounted_ro',
    'screenshot',
    'sensors',
    'sysinfo',
    'unlock_pacman',
    'uptime'
]
