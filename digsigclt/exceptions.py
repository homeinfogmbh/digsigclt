"""Common exceptions."""


__all__ = [
    'ManifestError',
    'UnderAdministration',
    'PackageManagerActive',
    'NoAddressFound',
    'UpdateProtocolError'
]


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
