"""Disk monitoring using SMART tools."""

from os import linesep
from subprocess import check_output
from typing import Generator

from digsigclt.os.posix.common import sudo


__all__ = ['device_states']


SMARTCTL = '/usr/bin/smartctl'
SEARCH_STRING = 'SMART overall-health self-assessment test result:'


def smartctl(*args: str) -> tuple:
    """Runs smartctl."""

    return sudo(SMARTCTL, *args)


def get_devices() -> Generator[str, None, None]:
    """Yields SMART capable devices."""

    text = check_output(smartctl('--scan-open'), text=True)

    for line in text.split(linesep):
        if line := line.strip():
            device, *_ = line.split()
            yield device


def check_device(device: str) -> str:
    """Checks the SMART status of the given device."""

    text = check_output(smartctl('-H', device), text=True)

    for line in text.split(linesep):
        if (line := line.strip()).startswith(SEARCH_STRING):
            _, result = line.split(':')
            return result

    return 'UNKNOWN'


def device_states() -> dict:
    """Checks the devices SMART status using smartctl."""

    return {device: check_device(device) for device in get_devices()}
