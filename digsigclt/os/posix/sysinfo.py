"""Miscellaneous system information."""

from typing import Any

from digsigclt.os.posix.application import Application, status, version
from digsigclt.os.posix.checkupdates import checkupdates
from digsigclt.os.posix.cmdline import cmdline
from digsigclt.os.posix.cpuinfo import cpuinfo, is_baytrail
from digsigclt.os.posix.meminfo import meminfo
from digsigclt.os.posix.mount import efi_mounted_as_boot
from digsigclt.os.posix.smartctl import device_states
from digsigclt.os.posix.uptime import uptime


__all__ = ['sysinfo']


def sysinfo() -> dict[str, Any]:
    """Return miscellaneous system information."""

    return {
        'application': {
            'status': status().to_json(),
            'version': version(Application.HTML)
        },
        'baytrail': is_baytrail(),
        'efi': {
            'mounted': efi_mounted_as_boot()
        },
        'cmdline': dict(cmdline()),
        'cpuinfo': list(cpuinfo()),
        'meminfo': dict(meminfo()),
        'smartctl': device_states(),
        'updates': checkupdates(),
        'uptime': uptime()
    }
