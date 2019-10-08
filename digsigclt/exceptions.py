"""Common exceptions."""


__all__ = [
    'ManifestError',
    'UnderAdministration',
    'PackageManagerActive',
    'NetworkError'
]


class ManifestError(Exception):
    """Indicates general errors with the files manifest."""


class UnderAdministration(Exception):
    """Indicates that the system is currently
    under administrative use, blocking an action.
    """


class PackageManagerActive(Exception):
    """Indicates that a running package manager is blocking an action."""


class NetworkError(Exception):
    """Indicates an error with the network configuration."""
