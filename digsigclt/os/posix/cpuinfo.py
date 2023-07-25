"""CPU-related functions."""

from contextlib import suppress
from pathlib import Path
from typing import Iterator


__all__ = ["cpuinfo", "is_baytrail"]


BAYTRAIL_CPUS = {
    "A1020",
    "E3805",
    "E3815",
    "E3825",
    "E3826",
    "E3827",
    "E3845",
    "J1750",
    "J1800",
    "J1850",
    "J1900",
    "J2850",
    "J2900",
    "N2805",
    "N2806",
    "N2807",
    "N2808",
    "N2810",
    "N2815",
    "N2820",
    "N2830",
    "N2840",
    "N2910",
    "N2920",
    "N2930",
    "N2940",
    "N3510",
    "N3520",
    "N3530",
    "N3540",
    "Z3735D",
    "Z3735E",
    "Z3735F",
    "Z3735G",
    "Z3736F",
    "Z3736G",
    "Z3740",
    "Z3740D",
    "Z3745",
    "Z3745D",
    "Z3770",
    "Z3770D",
    "Z3775",
    "Z3775D",
    "Z3785",
    "Z3795",
}
CPUINFO = Path("/proc/cpuinfo")
LIST_KEYS = {"bugs", "flags", "vmx flags"}
CPUInfoValue = str | int | float | list[str]


def parse(key: str, value: str) -> CPUInfoValue:
    """Parse a key / value pair."""

    if key in LIST_KEYS:
        return value.split()

    with suppress(ValueError):
        return int(value)

    with suppress(ValueError):
        return float(value)

    return value


def cpuinfo() -> Iterator[dict[str, CPUInfoValue]]:
    """Yield information about the built-in CPUs."""

    core = {}

    with CPUINFO.open("r", encoding="ascii") as file:
        for line in file:
            if line := line.strip():
                key, value = map(str.strip, line.split(":"))
                core[key] = parse(key, value)
            else:
                yield core
                core = {}


def is_baytrail() -> bool:
    """Check whether this system is a baytrail system."""

    return any(
        baytrail in cpu.get("model name")
        for baytrail in BAYTRAIL_CPUS
        for cpu in cpuinfo()
    )
