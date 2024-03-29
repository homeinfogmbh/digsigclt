"""Common exceptions."""

from os import linesep
from subprocess import CalledProcessError
from typing import Iterable


__all__ = [
    "CalledProcessErrors",
    "ManifestError",
    "NoAddressFound",
    "PackageManagerActive",
    "RequestError",
    "UnderAdministration",
    "UpdateProtocolError",
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
    """Indicate general errors with the files manifest."""


class NoAddressFound(Exception):
    """Indicate that no address matching
    the respective network could be found.
    """


class PackageManagerActive(Exception):
    """Indicate that a running package manager is blocking an action."""


class RequestError(Exception):
    """Indicate an error during handling of a HTTP request."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UnderAdministration(Exception):
    """Indicate that the system is currently
    under administrative use, blocking an action.
    """


class UpdateProtocolError(Exception):
    """Indicate an error within the update protocol."""

    def __init__(self, code: int):
        """Set the HTTP status code."""
        super().__init__()
        self.code = code
