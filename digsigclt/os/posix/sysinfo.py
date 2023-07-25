"""Miscellaneous system information."""

from typing import Any

from digsigclt.os.posix.application import status
from digsigclt.os.posix.cmdline import cmdline
from digsigclt.os.posix.cpuinfo import cpuinfo, is_baytrail
from digsigclt.os.posix.df import df
from digsigclt.os.posix.meminfo import meminfo
from digsigclt.os.posix.mount import efi_mounted_as_boot, root_mounted_ro
from digsigclt.os.posix.netstats import netstats
from digsigclt.os.posix.presentation import read_presentation
from digsigclt.os.posix.sensors import sensors
from digsigclt.os.posix.smartctl import device_states
from digsigclt.os.posix.uptime import uptime


__all__ = ["sysinfo"]


def sysinfo() -> dict[str, Any]:
    """Return miscellaneous system information."""

    return {
        "application": status().to_json(),
        "baytrail": is_baytrail(),
        "efi": {"mounted": efi_mounted_as_boot()},
        "cmdline": dict(cmdline()),
        "cpuinfo": list(cpuinfo()),
        "df": [item.to_json() for item in df(local=True, posix=True)],
        "meminfo": dict(meminfo()),
        "netstats": netstats(),
        "presentation": read_presentation(),
        "root_ro": root_mounted_ro(),
        "sensors": sensors(),
        "smartctl": device_states(),
        "uptime": uptime(),
    }
