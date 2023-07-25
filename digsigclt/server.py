"""HTTP server."""

from http.server import HTTPServer
from ipaddress import IPv6Address
from pathlib import Path
from socket import AF_INET6

from digsigclt.common import LOGGER
from digsigclt.request_handler import HTTPRequestHandler
from digsigclt.types import IPAddress, Socket


__all__ = ["spawn"]


class ImprovedHTTPServer(HTTPServer):
    """A better HTTP server."""

    def __init__(
        self,
        address: IPAddress,
        port: int,
        request_handler: type,
        bind_and_activate: bool = True,
    ):
        """Initialize the HTTP server with an IP address,
        port and request handler.
        """
        if isinstance(address, IPv6Address):
            self.address_family = AF_INET6

        socket = (str(address), port)
        super().__init__(socket, request_handler, bind_and_activate)


def spawn(socket: Socket, directory: Path, chunk_size: int) -> int:
    """Spawn an HTTP server."""

    class _RH(HTTPRequestHandler, chunk_size=chunk_size, directory=directory):
        """Implementation of the actual request handler."""

    httpd = ImprovedHTTPServer(*socket, _RH)
    LOGGER.info('Listening on "%s:%i".', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0
