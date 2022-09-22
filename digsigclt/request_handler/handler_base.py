"""Request handler base"""

from http.server import BaseHTTPRequestHandler
from json import loads
from typing import Any

from digsigclt.types import Payload, ResponseContent


__all__ = ['HTTPRequestHandlerBase']


class HTTPRequestHandlerBase(BaseHTTPRequestHandler):
    """Extension of the BaseHTTPRequestHandler with convenience methods."""

    @property
    def content_length(self) -> int:
        """Returns the content length."""
        return int(self.headers['Content-Length'])

    @property
    def bytes(self) -> bytes:
        """Returns sent JSON data."""
        return self.rfile.read(self.content_length)

    @property
    def json(self) -> Any:
        """Returns sent JSON data."""
        return loads(self.bytes)

    @property
    def remote_socket(self) -> tuple[str, int]:
        """Returns the remote socket."""
        return self.client_address[:2]

    def send_content(self, content: ResponseContent, status_code: int) -> None:
        """Sends the respective response content."""
        self.send_response(status_code)
        self.send_header('Content-Type', content.content_type)
        self.end_headers()
        self.wfile.write(content.payload)

    def send_data(
            self,
            payload: Payload,
            status_code: int,
            content_type: str | None = None
    ) -> None:
        """Sends the respective data."""
        self.send_content(
            ResponseContent.from_payload(payload, content_type=content_type),
            status_code
        )
