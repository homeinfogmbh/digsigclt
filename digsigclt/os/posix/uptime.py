"""Returns the uptime."""

from datetime import datetime, time, timedelta
from subprocess import check_output
from typing import NamedTuple


__all__ = ["uptime"]


UPTIME = "/usr/bin/uptime"


def parse_float(string: str) -> float:
    """Parse a float from a string."""

    return float(string.replace(",", "."))


def parse_timedelta(days: str | None, time_: str) -> timedelta:
    """Parse a timedelta from the given days and time."""

    if days:
        days, _ = days.split()
    else:
        days = 0

    if time_.endswith("min"):
        hours = 0
        minutes, _ = time_.split()
    else:
        hours, minutes = time_.split(":")

    return timedelta(days=int(days), hours=int(hours), minutes=int(minutes))


class Load(NamedTuple):
    """System load information."""

    past1: float
    past5: float
    past15: float

    @classmethod
    def from_string(cls, string: str):
        """Parses load from a substring of uptime."""
        _, load = string.split(": ")
        return cls(*map(parse_float, load.split(", ")))

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {"past1": self.past1, "past5": self.past5, "past15": self.past15}


class Uptime(NamedTuple):
    """System uptime."""

    timestamp: time
    uptime: timedelta
    users: int
    load: Load

    @classmethod
    def from_string(cls, string: str):
        """Returns the uptime information from a string."""
        uptime_, users, load = string.split(",", maxsplit=2)

        if users.endswith("user") or users.endswith("users"):
            time_ = None
        else:
            uptime_, time_, users, load = string.split(",", maxsplit=3)
            time_ = time_.strip()

        uptime_, users, load = uptime_.strip(), users.strip(), load.strip()
        timestamp, secondary = uptime_.split(" up ")
        timestamp = datetime.strptime(timestamp, "%H:%M:%S").time()

        if time_ is None:
            uptime_ = parse_timedelta(None, secondary)
        else:
            uptime_ = parse_timedelta(secondary, time_)

        users, _ = users.split()
        return cls(timestamp, uptime_, int(users), Load.from_string(load))

    @classmethod
    def get(cls):
        """Reads the uptime from the system."""
        return cls.from_string(check_output(UPTIME, text=True).strip())

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "uptime": self.uptime.total_seconds(),
            "users": self.users,
            "load": self.load.to_json(),
        }


def uptime() -> dict:
    """Return the system uptime."""

    return Uptime.get().to_json()
