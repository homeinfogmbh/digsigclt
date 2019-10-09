"""Common exceptions."""


__all__ = [
    'ManifestError',
    'UnderAdministration',
    'PackageManagerActive',
    'NoAddressFound',
    'AmbiguousAddressesFound'
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


class AmbiguousAddressesFound(Exception):
    """indicates that ambiguous addresses
    have been found on the respective network.
    """

    def __init__(self, addresses):
        """Sets the respective ambiguous addresses."""
        super().__init__()
        self.addresses = addresses
