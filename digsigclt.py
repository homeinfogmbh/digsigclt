#! /usr/bin/env python3
#
#  digsigclt - Digital Signage data synchronization client.
#
#  digsigclt is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  digsigclt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with digsigclt.  If not, see <http://www.gnu.org/licenses/>.
#
#  This unit provides a service to automatically login
#  the digital signage user to a certain terminal.
#
#  (C) 2019: HOMEINFO - Digitale Informationssysteme GmbH
#
#  Maintainer: Richard Neumann <r dot neumann at homeinfo period de>
#
#######################################################################
"""Digital signage cross-platform client."""

from argparse import ArgumentParser, Namespace
from contextlib import suppress
from datetime import datetime
from functools import partial
from hashlib import sha256
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from json import dumps, load, loads
from logging import DEBUG, INFO, basicConfig, getLogger
from os import linesep
from pathlib import Path
from sys import exit    # pylint: disable=W0622
from tarfile import open as tar_open
from tempfile import gettempdir, TemporaryDirectory
from threading import Lock
from typing import Iterable


DESCRIPTION = '''HOMEINFO multi-platform digital signage client.
Synchronizes data to the current working directory when triggered.'''
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGFILE = 'synclog.txt'
LOGGER = getLogger('digsigclt')
LOCK = Lock()


def get_files(directory: dict) -> Iterable[Path]:
    """Lists the current files."""

    for inode in directory.iterdir():
        if inode.is_dir():
            yield from get_files(inode)
        elif inode.is_file():
            yield inode


def copy_file(src_file: Path, dst_file: Path, *, chunk_size: int = 4096):
    """Copies a file from src to dst."""

    with src_file.open('rb') as src, dst_file.open('wb') as dst:
        for chunk in iter(partial(src.read, chunk_size), b''):
            dst.write(chunk)


def copydir(source_dir: Path, dest_dir: Path, *, chunk_size: int = 4096):
    """Copies all contents of source_dir
    into dest_dir, overwriting all files.
    """

    LOGGER.debug('Copying "%s" to "%s".', source_dir, dest_dir)

    for source_path in source_dir.iterdir():
        relpath = source_path.relative_to(source_dir)
        dest_path = dest_dir.joinpath(relpath)

        if source_path.is_file():
            LOGGER.info('Updating file "%s".', dest_path)
            copy_file(source_path, dest_path, chunk_size=chunk_size)
        elif source_path.is_dir():
            if dest_path.is_file():
                dest_path.unlink()

            dest_path.mkdir(mode=0o755, parents=True, exist_ok=True)
            copydir(source_path, dest_path, chunk_size=chunk_size)
        else:
            LOGGER.warning(
                'Skipping "%s" which is neither a file nor a directory.',
                source_path)


def strip_files(directory: Path, manifest: frozenset):
    """Removes all files from the directory tree,
    whose SHA-256 checksums are not in the manifest.
    """

    for path in get_files(directory):
        relpath = path.relative_to(directory)

        if str(relpath) not in manifest:
            LOGGER.debug('Removing obsolete file "%s".', path)
            path.unlink()


def strip_tree(directory: Path):
    """Removes all empty directory sub-trees."""

    def strip_subdir(subdir: Path):
        """Recursively removes empty directory trees."""
        for inode in subdir.iterdir():
            if inode.is_dir():
                strip_subdir(inode)

        if not tuple(subdir.iterdir()):     # Directory is empty.
            LOGGER.debug('Removing empty directory "%s".', subdir)
            subdir.rmdir()

    for inode in directory.iterdir():
        if inode.is_dir():
            strip_subdir(inode)


def load_manifest(tmpd: Path) -> frozenset:
    """Reads the manifest from the respective temporary directory."""

    path = tmpd.joinpath('manifest.json')
    LOGGER.debug('Reading manifest from "%s".', path)

    with path.open('r') as file:
        manifest = load(file)

    # Remove file to prevent it from being
    # copied to digital signage data directory.
    path.unlink()
    return frozenset(manifest)


def gen_manifest(directory: Path, chunk_size: int = 4096) -> Iterable[tuple]:
    """Yields tuples of all file's names and their
    respective SHA-256 sums in the given directory.
    """

    for filename in get_files(directory):
        sha256sum = sha256()

        with filename.open('rb') as file:
            for chunk in iter(partial(file.read, chunk_size), b''):
                sha256sum.update(chunk)

        sha256sum = sha256sum.hexdigest()
        LOGGER.debug('SHA-256 sum of "%s" is "%s".', filename, sha256sum)
        relpath = filename.relative_to(directory)
        yield (str(relpath), sha256sum)


def update(file: BytesIO, directory: Path, *, chunk_size: int = 4096) -> bool:
    """Updates the digital signage data
    from the respective tar.xz archive.
    """

    with TemporaryDirectory() as tmpd:
        LOGGER.debug('Extracting archive to "%s".', tmpd)

        with tar_open(mode='r:xz', fileobj=file, bufsize=chunk_size) as tar:
            tar.extractall(path=tmpd)

        tmpd = Path(tmpd)
        manifest = load_manifest(tmpd)

        try:
            copydir(tmpd, directory, chunk_size=chunk_size)
        except PermissionError as permission_error:
            LOGGER.critical(permission_error)
            return False

    strip_files(directory, manifest)
    strip_tree(directory)

    with Path(gettempdir()).joinpath(LOGFILE).open('a') as logfile:
        logfile.write(datetime.now().isoformat())
        logfile.write(linesep)

    return True


def server(socket: tuple, request_handler: BaseHTTPRequestHandler) -> int:
    """Runs the HTTP server."""

    httpd = HTTPServer(socket, request_handler)
    LOGGER.info('Listening on "%s:%i".', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0


def requesthandler(directory: Path, chunk_size: int) -> BaseHTTPRequestHandler:
    """Returns a HTTP request handler for the given arguments."""

    class RequestHandler(HTTPRequestHandler):   # pylint: disable=E0601
        """A configured version of the request
        handler with DIRECTORY and CHUNK_SIZE set.
        """
        DIRECTORY = directory
        CHUNK_SIZE = chunk_size

    return RequestHandler


def get_args() -> Namespace:
    """Returns the command line arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-a', '--address', default='0.0.0.0', metavar='address',
        help='IPv4 address to listen on')
    parser.add_argument(
        '-p', '--port', type=int, default=5000, metavar='port',
        help='port to listen on')
    parser.add_argument(
        '-d', '--directory', type=Path, metavar='dir', default=Path.cwd(),
        help='sets the target directory')
    parser.add_argument(
        '-c', '--chunk-size', type=int, default=4096, metavar='bytes',
        help='chunk size to use on file operations')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='turn on verbose logging')
    return parser.parse_args()


def main() -> int:
    """Main method to run."""

    args = get_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    LOGGER.debug('Target directory set to "%s".', args.directory)

    if args.directory.is_dir():
        socket = (args.address, args.port)
        request_handler = requesthandler(args.directory, args.chunk_size)
        return server(socket, request_handler)

    LOGGER.critical('Target directory "%s" does not exist.', args.directory)
    return 2


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    LAST_SYNC = None
    DIRECTORY = NotImplemented
    CHUNK_SIZE = NotImplemented

    @property
    def last_sync(self) -> datetime:
        """Returns the datetime of the last sync."""
        return type(self).LAST_SYNC

    @last_sync.setter
    def last_sync(self, last_sync: datetime):
        """Sets the datetime of the last sync."""
        type(self).LAST_SYNC = last_sync

    @property
    def directory(self) -> Path:
        """Returns the working directory."""
        return type(self).DIRECTORY

    @property
    def chunk_size(self) -> Path:
        """Returns the chunk size for file operations."""
        return type(self).CHUNK_SIZE

    @property
    def content_length(self) -> int:
        """Returns the content length."""
        return int(self.headers['Content-Length'])

    @property
    def bytes(self) -> bytes:
        """Returns the POST-ed bytes."""
        return self.rfile.read(self.content_length)

    @property
    def json(self) -> dict:
        """Returns received JSON data."""
        return loads(self.bytes)

    @property
    def manifest(self):
        """Returns the manifest."""
        if LOCK.acquire():
            manifest = gen_manifest(self.directory, chunk_size=self.chunk_size)
            manifest = dict(manifest)
            LOCK.release()
            return manifest

        return None

    def send_data(self, value, status_code: int, content_type: str = None):
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

    def update_digsig_data(self):
        """Updates the digital signage data."""
        try:
            file = BytesIO(self.bytes)
        except MemoryError:
            LOGGER.critical('Received file is too large.')
            status_code = 507   # Insufficient Storage.
            body = 'File cannot be processed due to insufficient memory.'
            return self.send_data(body, status_code)

        if update(file, self.directory, chunk_size=self.chunk_size):
            text = 'System synchronized.'
            status_code = 200
            self.last_sync = datetime.now()
        else:
            text = 'Synchronization failed.'
            status_code = 500

        return self.send_data(text, status_code)

    def do_GET(self):   # pylint: disable=C0103
        """Returns current status information."""
        manifest = self.manifest

        if manifest is None:
            return self.send_data('System is currently locked.', 503)

        json = {'manifest': manifest}

        if self.last_sync is not None:
            json['last_sync'] = self.last_sync.isoformat()

        return self.send_data(json, 200)

    def do_POST(self):  # pylint: disable=C0103
        """Retrieves and updates digital signage data."""
        if LOCK.acquire():
            self.update_digsig_data()
            LOCK.release()
        else:
            self.send_data('Synchronization already in progress.', 503)


if __name__ == '__main__':
    exit(main())
