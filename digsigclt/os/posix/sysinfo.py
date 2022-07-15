"""Miscellaneous system information."""

from typing import Any

from digsigclt.os.posix.application import running, status, version
from digsigclt.os.posix.cmdline import cmdline
from digsigclt.os.posix.cpuinfo import cpuinfo, is_baytrail
from digsigclt.os.posix.meminfo import meminfo
from digsigclt.os.posix.mount import efi_mounted_as_boot, root_mounted_ro
from digsigclt.os.posix.presentation import read_presentation
from digsigclt.os.posix.sensors import sensors
from digsigclt.os.posix.smartctl import device_states
from digsigclt.os.posix.uptime import uptime


__all__ = ['sysinfo']


def sysinfo() -> dict[str, Any]:
    """Return miscellaneous system information."""

    return {
        'application': {
            'status': status().to_json(),
            'version': version(running())
        },
        'baytrail': is_baytrail(),
        'efi': {
            'mounted': efi_mounted_as_boot()
        },
        'cmdline': dict(cmdline()),
        'cpuinfo': list(cpuinfo()),
        'meminfo': dict(meminfo()),
        'presentation': read_presentation(),
        'root_ro': root_mounted_ro(),
        'sensors': sensors(),
        'smartctl': device_states(),
        'uptime': uptime()
    }
