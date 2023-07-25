"""Temperature sensors readout."""

from json import loads
from subprocess import CalledProcessError, check_output
from typing import Any


__all__ = ["sensors"]


SENSORS = "/usr/bin/sensors"


def sensors() -> dict[str, Any] | None:
    """Read out sensors."""

    try:
        return loads(check_output([SENSORS, "-j"], text=True))
    except CalledProcessError:
        return None
