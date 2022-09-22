"""Common exceptions."""

from os import linesep
from subprocess import CalledProcessError
from typing import Iterable


__all__ = [
    'CalledProcessErrors',
    'ManifestError',
    'UnderAdministration',
    'PackageManagerActive',
    'NoAddressFound',
    'UpdateProtocolError'
]


class CalledProcessErrors(Exception):
    """Collection of multiple called process errors."""

    def __init__(self, called_process_errors: Iterable[CalledProcessError]):
        """Sets the called process errors."""
        super().__init__()
        self.called_process_errors = list(called_process_errors)

    def __str__(self):
        return linesep.join(map(str, self.called_process_errors))


class ManifestError(Exception):
    """Indicates general errors with the files manifest."""


class UnderAdministration(Exception):
    """Indicates that the system is currently
    under administrative use, blocking an action.
    """


class PackageManagerActive(Exception):
    """Indicates that a running package manager is blocking an action."""


class NoAddressFound(Exception):
    """Indicates that no address matching
    the respective network could be found.
    """


class UpdateProtocolError(Exception):
    """Indicates an error within the update protocol."""

    def __init__(self, code: int):
        """Sets the HTTP status code."""
        super().__init__()
        self.code = code
