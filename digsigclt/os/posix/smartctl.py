"""Disk monitoring using SMART tools."""

from os import linesep
from subprocess import check_output
from typing import Iterator

from digsigclt.os.posix.common import sudo


__all__ = ["device_states"]


SMARTCTL = "/usr/bin/smartctl"
SEARCH_STRING = "SMART overall-health self-assessment test result:"


def smartctl(*args: str) -> list[str]:
    """Run smartctl."""

    return sudo(SMARTCTL, *args)


def get_devices() -> Iterator[str]:
    """Yield SMART capable devices."""

    text = check_output(smartctl("--scan-open"), text=True)

    for line in text.split(linesep):
        if line := line.strip():
            device, *_ = line.split()
            yield device


def check_device(device: str) -> str:
    """Check the SMART status of the given device."""

    text = check_output(smartctl("-H", device), text=True)

    for line in text.split(linesep):
        if (line := line.strip()).startswith(SEARCH_STRING):
            _, result = line.split(":")
            return result.strip()

    return "UNKNOWN"


def device_states() -> dict:
    """Check the devices SMART status using smartctl."""

    return {device: check_device(device) for device in get_devices()}
