"""Implements a basic http request handler."""

from contextlib import suppress
from datetime import datetime
from os import linesep, name
from pathlib import Path
from tempfile import TemporaryFile

from digsigclt.common import LOGFILE, LOGGER, copy_file
from digsigclt.lock import Locked
from digsigclt.rpc import COMMANDS, http_screenshot
from digsigclt.os import application_status, sysinfo
from digsigclt.sync import update

from digsigclt.request_handler.common import LOCK
from digsigclt.request_handler.functions import get_manifest
from digsigclt.request_handler.handler_base import HTTPRequestHandlerBase


__all__ = ['HTTPRequestHandler']


class HTTPRequestHandler(HTTPRequestHandlerBase):
    """HTTP request handler with additional properties and functions."""

    last_sync = None

    def __init_subclass__(cls, *, chunk_size: int, directory: Path):
        """Initializes the subclass."""
        cls.chunk_size = chunk_size
        cls.directory = directory

    @property
    def logfile(self) -> Path:
        """Returns the log file."""
        return self.directory / LOGFILE

    def send_sysinfo(self) -> None:
        """Returns system information."""
        if (last_sync := type(self).last_sync) is not None:
            last_sync = last_sync.isoformat()

        json = {'lastSync': last_sync}

        with suppress(NotImplementedError):
            json.update(sysinfo())

        self.send_data(json, 200)

    def log_sync(self) -> None:
        """Logs the synchronization."""
        type(self).last_sync = last_sync = datetime.now()

        with self.logfile.open('w') as logfile:
            logfile.write(last_sync.isoformat())

            if name == 'posix':
                logfile.write(linesep)

    def update_digsig_data(self) -> None:
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

        self.send_data(text, status_code)

    def send_manifest(self) -> None:
        """Sends the manifest."""
        LOGGER.info('Manifest queried from %s:%s.', *self.remote_socket)

        if (manifest := get_manifest(self.directory, self.chunk_size)) is None:
            text = 'System is currently locked.'
            LOGGER.error(text)
            self.send_data(text, 503)
            return

        json = {'manifest': manifest}

        with suppress(NotImplementedError):
            json['application'] = application_status().to_json()

        if (last_sync := type(self).last_sync) is not None:
            json['last_sync'] = last_sync.isoformat()

        LOGGER.debug('Sending manifest.')
        self.send_data(json, 200)

    def send_screenshot(self) -> None:
        """Sends an HTTP screenshot."""
        LOGGER.info('Screenshot queried from %s:%s.', *self.remote_socket)

        try:
            payload, content_type, status_code = http_screenshot()
        except Exception as error:
            json = {'message': str(error), 'type': str(type(error))}
            self.send_data(json, 500)
            return

        self.send_data(payload, status_code, content_type)

    def do_GET(self) -> None:
        """Returns current status information."""
        if self.path in {'', '/'}:
            self.send_sysinfo()
            return

        if self.path == '/manifest':
            self.send_manifest()
            return

        if self.path == '/screenshot':
            self.send_screenshot()
            return

        self.send_data('Invalid path.', 404)

    def do_POST(self) -> None:
        """Retrieves and updates digital signage data."""
        LOGGER.info('Incoming sync from %s:%s.', *self.remote_socket)

        try:
            with LOCK:
                self.update_digsig_data()
        except Locked:
            text = 'Synchronization already in progress.'
            LOGGER.error(text)
            self.send_data(text, 503)

    def do_PUT(self) -> None:
        """Handles special commands."""
        LOGGER.info('Incoming command from %s:%s.', *self.remote_socket)

        try:
            json = self.json
        except MemoryError:
            LOGGER.error('Out of memory.')
            self.send_data('Out of memory.', 500)
            return
        except ValueError:
            LOGGER.warning('Received data is not JSON.')
            self.send_data('Received data is not JSON.', 406)
            return

        try:
            command = json.pop('command')
        except KeyError:
            LOGGER.warning('No command specified.')
            self.send_data('No command specified.', 400)
            return

        LOGGER.debug('Received command: "%s".', command)

        try:
            function = COMMANDS[command]
        except KeyError:
            LOGGER.warning('Invalid command specified: "%s".', command)
            self.send_data('Invalid command specified.', 400)
            return

        LOGGER.debug('Executing function "%s" with args "%s".', function, json)

        try:
            response = function(**json)
        except TypeError:
            LOGGER.warning('Invalid arguments specified: "%s".', json)
            self.send_data('Invalid arguments specified.', 400)
            return

        LOGGER.debug('Function returned: "%s".', response)
        self.send_data(
            response.payload,
            response.status_code,
            content_type=response.content_type
        )
