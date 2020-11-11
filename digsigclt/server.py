"""HTTP server."""

from http.server import HTTPServer
from pathlib import Path

from digsigclt.common import LOGGER
from digsigclt.request_handler import HTTPRequestHandler
from digsigclt.types import Socket


__all__ = ['spawn']


# pylint: disable=W0613
def spawn(socket: Socket, directory: Path, chunk_size: int) -> int:
    """Spawns a HTTP server."""

    class _RH(HTTPRequestHandler, chunk_size=chunk_size, directory=directory):
        """Implementation of the actual request handler."""

    httpd = HTTPServer(socket.compat(), _RH)
    LOGGER.info('Listening on "%s:%i".', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0
