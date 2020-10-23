"""HTTP server."""

from http.server import HTTPServer
from pathlib import Path
from typing import Callable, Tuple

from digsigclt.common import LOGGER
from digsigclt.request_handler import HTTPRequestHandler


__all__ = ['spawn']


def run_server(socket: Tuple[str, int], request_handler: Callable) -> int:
    """Runs the HTTP server."""

    httpd = HTTPServer(socket, request_handler)
    LOGGER.info('Listening on "%s:%i".', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0


def spawn(socket: Tuple[str, int], directory: Path, chunk_size: int):
    """Spawns a HTTP server."""

    class _HTTPRequestHandler(HTTPRequestHandler, directory, chunk_size):
        pass

    return run_server(socket, _HTTPRequestHandler)
