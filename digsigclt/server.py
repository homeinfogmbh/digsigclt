"""HTTP server."""

from http.server import HTTPServer
from pathlib import Path

from digsigclt.common import LOGGER
from digsigclt.request_handler import HTTPRequestHandler
from digsigclt.types import Socket


__all__ = ['spawn']


def spawn(socket: Socket, directory: Path, chunk_size: int) -> int:
    """Spawns a HTTP server."""

    class _HTTPRequestHandler(HTTPRequestHandler, directory, chunk_size):
        pass

    httpd = HTTPServer(socket.compat(), _HTTPRequestHandler)
    LOGGER.info('Listening on "%s:%i".', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0
