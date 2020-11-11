"""Implements a basic http request handler."""

from contextlib import suppress
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from json import dumps, loads
from os import linesep, name
from pathlib import Path
from tempfile import TemporaryFile
from typing import NamedTuple

from digsigclt.common import CHUNK_SIZE, LOGFILE, LOGGER
from digsigclt.io import copy_file
from digsigclt.lock import Locked, Lock
from digsigclt.rpc import COMMANDS
from digsigclt.os import uptime
from digsigclt.sync import gen_manifest, update


__all__ = ['HTTPRequestHandler']


LOCK = Lock()


class ResponseContent(NamedTuple):
    """A HTTP response content."""

    payload: bytes
    content_type: str


def get_manifest(directory: Path, chunk_size: int = CHUNK_SIZE) -> list:
    """Returns the manifest."""

    with suppress(Locked):
        with LOCK.acquire:
            return gen_manifest(directory, chunk_size=chunk_size)

    return None


def format_response(payload, content_type: str) -> ResponseContent:
    """Detects the content type and formats the HTTP payload accordingly."""

    if payload is None:
        payload = dumps(payload)
        content_type = content_type or 'application/json'
    elif isinstance(payload, (dict, list)):
        payload = dumps(payload)
        content_type = content_type or 'application/json'
    elif isinstance(payload, str):
        content_type = content_type or 'text/plain'

    with suppress(AttributeError):
        payload = payload.encode()

    return ResponseContent(payload, content_type)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler with additional properties and functions."""

    chunk_size = None
    directory = None
    last_sync = None

    @property
    def logfile(self):
        """Returns the log file."""
        return self.directory.joinpath(LOGFILE)     # pylint: disable=E1101

    @property
    def content_length(self):
        """Returns the content length."""
        return int(self.headers['Content-Length'])

    @property
    def bytes(self):
        """Returns sent bytes."""
        return self.rfile.read(self.content_length)

    @property
    def text(self):
        """Returns sent text."""
        return self.bytes.decode()

    @property
    def json(self):
        """Returns sent JSON data."""
        return loads(self.bytes)

    def send_data(self, payload, status_code: int, content_type: str = None):
        """Sends the respective data."""
        payload, content_type = format_response(payload, content_type)
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(payload)

    def send_sysinfo(self):
        """Returns system information."""
        if (last_sync := type(self).last_sync) is None:
            last_sync = None
        else:
            last_sync = last_sync.isoformat()

        json = {'lastSync': last_sync}

        with suppress(NotImplementedError):
            json['uptime'] = uptime()

        self.send_data(json, 200)

    def log_sync(self):
        """Logs the synchronization."""
        type(self).last_sync = last_sync = datetime.now()

        with self.logfile.open('w') as logfile:
            logfile.write(last_sync.isoformat())

            if name == 'posix':
                logfile.write(linesep)

    def update_digsig_data(self):
        """Updates the digital signage data."""
        with TemporaryFile('w+b') as file:
            copy_file(self.rfile, file, self.content_length, self.chunk_size)
            LOGGER.debug('Flushing temporary file.')
            file.flush()
            file.seek(0)

            if update(file, self.directory, chunk_size=self.chunk_size):
                text = 'System synchronized.'
                status_code = 200
                self.log_sync()
                LOGGER.info(text)
            else:
                text = 'Synchronization failed.'
                status_code = 500
                LOGGER.error(text)

        return self.send_data(text, status_code)

    def send_manifest(self):
        """Sends the manifest."""
        LOGGER.info('Incoming manifest query from %s:%s.',
                    *self.client_address)

        if (manifest := get_manifest(self.directory, self.chunk_size)) is None:
            text = 'System is currently locked.'
            LOGGER.error(text)
            return self.send_data(text, 503)

        json = {'manifest': manifest}

        if (last_sync := type(self).last_sync) is not None:
            json['last_sync'] = last_sync.isoformat()

        LOGGER.debug('Sending manifest.')
        return self.send_data(json, 200)

    def do_GET(self):   # pylint: disable=C0103
        """Returns current status information."""
        if self.path in {'', '/'}:
            return self.send_sysinfo()

        if self.path == '/manifest':
            return self.send_manifest()

        return self.send_data('Invalid path.', 404)

    def do_POST(self):  # pylint: disable=C0103
        """Retrieves and updates digital signage data."""
        LOGGER.info('Incoming sync from %s:%s.', *self.client_address)

        try:
            with LOCK:
                self.update_digsig_data()
        except Locked:
            text = 'Synchronization already in progress.'
            LOGGER.error(text)
            self.send_data(text, 503)

    def do_PUT(self):  # pylint: disable=C0103,R0911
        """Handles special commands."""
        LOGGER.info('Incoming command from %s:%s.', *self.client_address)

        try:
            json = self.json
        except MemoryError:
            LOGGER.error('Out of memory.')
            return self.send_data('Out of memory.', 500)
        except ValueError:
            LOGGER.warning('Received data is not JSON.')
            return self.send_data('Received data is not JSON.', 406)

        try:
            command = json.pop('command')
        except KeyError:
            LOGGER.warning('No command specified.')
            return self.send_data('No command specified.', 400)

        LOGGER.debug('Received command: "%s".', command)

        try:
            function = COMMANDS[command]
        except KeyError:
            LOGGER.warning('Invalid command specified: "%s".', command)
            return self.send_data('Invalid command specified.', 400)

        LOGGER.debug('Executing function "%s" with args "%s".', function, json)

        try:
            result = function(**json)
        except TypeError:
            LOGGER.warning('Invalid arguments specified: "%s".', json)
            return self.send_data('Invalid arguments specified.', 400)

        LOGGER.debug('Function returned: "%s".', result)

        try:
            payload, content_type, status_code = result
        except (TypeError, ValueError):
            LOGGER.warning('Internal function returned garbage: "%s".', result)
            return self.send_data('Internal function returned garbage.', 500)

        LOGGER.debug('Sending "%s" with status "%s".', payload, status_code)
        return self.send_data(payload, status_code, content_type=content_type)
