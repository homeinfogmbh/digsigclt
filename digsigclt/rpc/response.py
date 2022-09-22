"""RPC related utilities."""

from dataclasses import dataclass
from subprocess import CalledProcessError

from digsigclt.exceptions import CalledProcessErrors
from digsigclt.exceptions import UnderAdministration
from digsigclt.exceptions import PackageManagerActive
from digsigclt.types import Payload


__all__ = ['Response']


ERRORS = {
    ValueError: lambda error: (', '.join(error.args), 400),
    NotImplementedError:
        lambda error: ('Action is not implemented on this platform.', 501),
    CalledProcessError: lambda error: (str(error), 500),
    CalledProcessErrors: lambda error: (str(error), 500),
    UnderAdministration:
        lambda error: ('The system is currently under administration.', 503),
    PackageManagerActive:
        lambda error: ('The package manager is currently running.', 503)
}


@dataclass
class Response:
    """Represents response data with error handling capability."""

    payload: Payload = None
    content_type: str = 'application/json'
    status_code: int = 200

    def __enter__(self):
        """Enters a context and returns itself."""
        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        try:
            function = ERRORS[typ]
        except KeyError:
            return False

        self.message, self.status_code = function(value)
        return True

    def __iter__(self):
        """Yields the properties."""
        yield self.payload
        yield self.content_type
        yield self.status_code

    @property
    def message(self):
        """Returns the JSON message if set."""
        try:
            return self.payload.get('message')
        except AttributeError:
            return None

    @message.setter
    def message(self, message: str):
        """Sets the payload to a JSON message
        and the content type to JSON.
        """
        self.payload = {'message': message}
        self.content_type = 'application/json'
