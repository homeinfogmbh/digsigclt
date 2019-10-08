"""Logging facility."""

from collections import namedtuple
from ipaddress import IPv4Network
from logging import getLogger
from pathlib import Path
from sys import argv


__all__ = [
    'CHUNK_SIZE',
    'LOG_FORMAT',
    'LOGFILE',
    'LOGGER',
    'TERMINAL_NETWORK',
    'ServiceState'
]


CHUNK_SIZE = 4 * 1024 * 1024    # Four Mebibytes.
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGFILE = Path('synclog.txt')
LOGGER = getLogger(Path(argv[0]).name)
TERMINAL_NETWORK = IPv4Network('10.8.0.0/16')
ServiceState = namedtuple('ServiceStatus', ('enabled', 'running'))
