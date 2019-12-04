"""HTTP server."""

from contextlib import suppress
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from json import dumps, loads
from os import linesep, name
from tempfile import TemporaryFile
from threading import Lock

from digsigclt.common import LOGFILE, LOGGER
from digsigclt.rpc import COMMANDS
from digsigclt.sync import gen_manifest, update


__all__ = ['spawn']


LOCK = Lock()


def run_server(socket, request_handler):
    """Runs the HTTP server."""

    httpd = HTTPServer(socket, request_handler)
    LOGGER.info('Listening on "%s:%i".', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0


def get_request_handler(directory, chunk_size):
    """Returns a HTTP request handler for the given arguments."""

    class RequestHandler(HTTPRequestHandler):   # pylint: disable=E0601
        """A configured version of the request
        handler with DIRECTORY and CHUNK_SIZE set.
        """
        DIRECTORY = directory
        CHUNK_SIZE = chunk_size

    return RequestHandler


def spawn(socket, directory, chunk_size):
    """Spawns a HTTP server."""

    return run_server(socket, get_request_handler(directory, chunk_size))


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    LAST_SYNC = None
    DIRECTORY = NotImplemented
    CHUNK_SIZE = NotImplemented

    @property
    def last_sync(self):
        """Returns the datetime of the last sync."""
        return type(self).LAST_SYNC

    @last_sync.setter
    def last_sync(self, last_sync):
        """Sets the datetime of the last sync."""
        type(self).LAST_SYNC = last_sync

    @property
    def directory(self):
        """Returns the working directory."""
        return type(self).DIRECTORY

    @property
    def logfile(self):
        """Returns the log file."""
        return self.directory.joinpath(LOGFILE)     # pylint: disable=E1101

    @property
    def chunk_size(self):
        """Returns the chunk size for file operations."""
        return type(self).CHUNK_SIZE

    @property
    def content_length(self):
        """Returns the content length."""
        return int(self.headers['Content-Length'])

    @property
    def json(self):
        """Returns sent JSON data."""
        return loads(self.rfile.read(self.content_length))

    @property
    def manifest(self):
        """Returns the manifest."""
        if LOCK.acquire():
            manifest = gen_manifest(self.directory, chunk_size=self.chunk_size)
            LOCK.release()
            return manifest

        return None

    def send_data(self, value, status_code, content_type=None):
        """Sends the respective data."""
        if isinstance(value, (dict, list)):
            value = dumps(value)
            content_type = content_type or 'application/json'
        elif isinstance(value, str):
            content_type = content_type or 'text/plain'

        with suppress(AttributeError):
            body = value.encode()

        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(body)

    def log_sync(self):
        """Logs the synchronization."""
        self.last_sync = last_sync = datetime.now()

        with self.logfile.open('w') as logfile:
            logfile.write(last_sync.isoformat())

            if name == 'posix':
                logfile.write(linesep)

    def read_to_file(self, file):
        """Reads the POSTed bytes and writes
        them to the given opened file object.
        """
        chunk_size = self.chunk_size
        remaining_bytes = self.content_length
        chunks = 0

        while remaining_bytes > 0:
            bytec = min(remaining_bytes, chunk_size)
            chunks += 1
            remaining_bytes -= bytec
            LOGGER.debug('Processing chunk #%i of %i bytes.', chunks, bytec)
            file.write(self.rfile.read(bytec))

    def update_digsig_data(self):
        """Updates the digital signage data."""
        with TemporaryFile('w+b') as file:
            self.read_to_file(file)
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

    def do_GET(self):   # pylint: disable=C0103
        """Returns current status information."""
        LOGGER.info('Incoming manifest query from %s:%s.',
                    *self.client_address)
        manifest = self.manifest

        if manifest is None:
            text = 'System is currently locked.'
            LOGGER.error(text)
            return self.send_data(text, 503)

        json = {'manifest': manifest}

        if self.last_sync is not None:
            json['last_sync'] = self.last_sync.isoformat()

        LOGGER.debug('Sending manifest.')
        return self.send_data(json, 200)

    def do_POST(self):  # pylint: disable=C0103
        """Retrieves and updates digital signage data."""
        LOGGER.info('Incoming sync from %s:%s.', *self.client_address)

        if LOCK.acquire():
            self.update_digsig_data()
            LOCK.release()
        else:
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
            text, status_code = result
        except (TypeError, ValueError):
            LOGGER.warning('Internal function returned garbage: "%s".', result)
            return self.send_data('Internal function returned garbage.', 500)

        LOGGER.debug('Sending text "%s" with status "%s".', text, status_code)
        return self.send_data(text, status_code)
