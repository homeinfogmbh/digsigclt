"""RPC related utilities."""

from json import loads, dumps
from subprocess import CalledProcessError

from digsigclt.exceptions import UnderAdministration, PackageManagerActive


__all__ = ['JSONResponse']


class JSONResponse:
    """Handles common exceptions and returns a JSON response."""

    def __init__(self, json=None, status_code=200):
        """Sets initial json value and status code."""
        self.json = json
        self.status_code = status_code

    def __enter__(self):
        """Enters a context and returns itself."""
        return self

    def __exit__(self, typ, value, traceback):
        """Handles the respective exceptions."""
        if typ is NotImplementedError:
            message = 'Beeping is not implemented on this platform.'
            self.status_code = 501
        elif typ is CalledProcessError:
            message = str(value)
            self.status_code = 500
        elif typ is UnderAdministration:
            message = 'The system is currently under administration.'
            self.status_code = 503
        elif typ is PackageManagerActive:
            message = 'The package manager is currently running.'
            self.status_code = 503
        else:
            return False

        self.json = {'message': message}
        return True

    @property
    def text(self):
        """Returns a JSON-ish text."""
        return dumps(self.json)

    @text.setter
    def text(self, text):
        """Sets a JSON-ish text."""
        self.json = loads(text)

    def __iter__(self):
        """Returns the text and status code."""
        yield self.text
        yield self.status_code
