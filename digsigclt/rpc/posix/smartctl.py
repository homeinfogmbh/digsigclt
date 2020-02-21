"""Disk monitoring using SMART tools."""

from os import linesep
from subprocess import check_output

from digsigclt.rpc.posix.common import sudo


__all__ = ['device_states']


SMARTCTL = '/usr/bin/smartctl'
SEARCH_STRING = 'SMART overall-health self-assessment test result:'


def smartctl(*args):
    """Runs smartctl."""

    return sudo(SMARTCTL, *args)


def get_devices():
    """Yields SMART capable devices."""

    # pylint: disable=E1123
    text = check_output(smartctl('--scan-open'), text=True)

    for line in text.split(linesep):
        line = line.strip()

        if line:
            device, *_ = line.split()
            yield device


def check_device(device):
    """Checks the SMART status of the given device."""

    # pylint: disable=E1123
    text = check_output(smartctl('-H', device), text=True)

    for line in text.split(linesep):
        line = line.strip()

        if line.startswith(SEARCH_STRING):
            _, result = line.split(':')
            return result

    return 'UNKNOWN'


def device_states():
    """Checks the devices SMART status using smartctl."""

    return {device: check_device(device) for device in get_devices()}
