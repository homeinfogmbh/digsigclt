"""RPC related utilities."""

from subprocess import CalledProcessError

from digsigclt.exceptions import UnderAdministration, PackageManagerActive
from digsigclt.types import Payload


__all__ = ['Response']


ERRORS = {
    ValueError: lambda error: (', '.join(error.args), 400),
    NotImplementedError: lambda error: (
        'Beeping is not implemented on this platform.', 501),
    CalledProcessError: lambda error: (str(error), 500),
    UnderAdministration: lambda error: (
        'The system is currently under administration.', 503),
    PackageManagerActive: lambda error: (
        'The package manager is currently running.', 503)
}


class Response:
    """Handles common exceptions and returns a JSON response."""

    def __init__(self, payload: Payload = None,
                 content_type: str = 'application/json',
                 status_code: int = 200):
        """Sets initial json value and status code."""
        self.payload = payload
        self.content_type = content_type
        self.status_code = status_code

    def __enter__(self):
        """Enters a context and returns itself."""
        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        try:
            function = ERRORS[typ]
        except KeyError:
            return False

        message, self.status_code = function(value)
        self.payload = {'message': message}
        self.content_type = 'application/json'
        return True

    def __iter__(self):
        """Returns the text and status code."""
        yield self.payload
        yield self.content_type
        yield self.status_code
