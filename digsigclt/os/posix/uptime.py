"""Returns the uptime."""

from datetime import datetime, time, timedelta
from subprocess import check_output
from typing import NamedTuple


__all__ = ['uptime']


UPTIME = '/usr/bin/uptime'


def parse_float(string: str) -> float:
    """Parses a float from a string."""

    return float(string.replace(',', '.'))


def parse_timedelta(days, time_):
    """Parses a timedelta from the given days and time."""

    if days:
        days, _ = days.split()

    if time_.endswith('min'):
        hours = 0
        minutes, _ = time_.split()
    else:
        hours, minutes = time_.split(':')

    return timedelta(days=int(days), hours=int(hours), minutes=int(minutes))


class Load(NamedTuple):
    """System load information."""

    max: float
    avg: float
    min: float

    @classmethod
    def from_string(cls, string: str):
        """Parses load from a substring of uptime."""
        _, load = string.split(': ')
        return cls(map(parse_float, load.split(', ')))

    def to_json(self):
        """Returns a JSON-ish dict."""
        return {
            'max': self.max,
            'avg': self.avg,
            'min': self.min
        }


class Uptime(NamedTuple):
    """Reprensents uptime data."""

    timestamp: time
    uptime: timedelta
    users: int
    load: Load

    @classmethod
    def from_string(cls, string: str):
        """Returns the uptime information from a string."""
        uptime_, users, load = string.split(',', maxsplit=2)

        if users.endswith('user') or users.endswith('users'):
            time_ = None
        else:
            uptime_, time_, users, load = string.split(',', maxsplit=3)
            time_ = time_.strip()

        uptime_, users, load = uptime_.strip(), users.strip(), load.strip()
        timestamp, secondary = uptime_.split(' up ')
        timestamp = datetime.strptime(timestamp, '%H:%M:%S').time()

        if time_ is None:
            uptime_ = parse_timedelta(0, secondary)
        else:
            uptime_ = parse_timedelta(secondary, time_)

        users, _ = users.split()
        return cls(timestamp, uptime_, int(users), Load.from_string(load))

    @classmethod
    def get(cls):
        """Reads the uptime from the system."""
        return cls.from_string(check_output(UPTIME, text=True).strip())

    def to_json(self):
        """Returns a JSON-ish dict."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'uptime': self.uptime.total_seconds(),
            'users': self.users,
            'load': self.load.to_json()
        }


def uptime() -> dict:
    """Returns the system uptime."""

    return Uptime.get().to_json()
