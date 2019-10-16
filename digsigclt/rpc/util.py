"""RPC related utilities."""

from subprocess import CalledProcessError

from digsigclt.exceptions import UnderAdministration, PackageManagerActive


__all__ = ['ExceptionHandler']


class ExceptionHandler:
    """Handles common exceptions."""

    def __init__(self, text, status_code=200):
        """Sets initial text and status code."""
        self.text = text
        self.status_code = status_code

    def __enter__(self):
        """Enters a context and returns itself."""
        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        if typ is NotImplementedError:
            self.text = 'Beeping is not implemented on this platform.'
            self.status_code = 501
        elif typ is CalledProcessError:
            self.text = str(value)
            self.status_code = 500
        elif typ is UnderAdministration:
            self.text = 'The system is currently under administration.'
            self.status_code = 503
        elif typ is PackageManagerActive:
            self.text = 'The package manager is currently running.'
            self.status_code = 503
        else:
            return False

        return True

    def __iter__(self):
        """Returns the text and status code."""
        yield self.text
        yield self.status_code
