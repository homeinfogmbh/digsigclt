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
from functools import partial
from hashlib import sha256
from http.server import HTTPServer, BaseHTTPRequestHandler
from json import dumps, load
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from sys import exit    # pylint: disable=W0622
from tarfile import open as tar_open
from tempfile import gettempdir, TemporaryDirectory
from typing import BinaryIO, Iterable


DESCRIPTION = '''HOMEINFO multi-platform digital signage client.
Synchronizes data to the current working directory
or listens on the specified port when in server mode
to be triggered to do so.'''
LOCKFILE_NAME = 'digsigclt.sync.lock'
MANIFEST_FILENAME = 'manifest.json'
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger('digsigclt')
RUNTIME = {}


class Locked(Exception):
    """Indicates that the synchronization is currently locked."""


def get_files(directory: dict) -> Iterable[Path]:
    """Lists the current files."""

    for inode in directory.iterdir():
        if inode.is_dir():
            yield from get_files(inode)
        elif inode.is_file():
            yield inode


def copy_file(src_file: Path, dst_file: Path, *, chunk_size: int = 4096):
    """Copies a file from src to dst."""

    with src_file.open('wb') as dst, dst_file.open('rb') as src:
        for chunk in iter(partial(src.read, chunk_size), b''):
            dst.write(chunk)


def copydir(source_dir: Path, dest_dir: Path, *, chunk_size: int = 4096):
    """Copies all contents of source_dir
    into dest_dir, overwriting all files.
    """

    for source_path in source_dir.iterdir():
        relpath = source_path.relative_to(source_dir)
        dest_path = dest_dir.joinpath(relpath)

        if source_path.is_file():
            LOGGER.info('Updating: %s.', dest_path)
            copy_file(dest_path, source_path, chunk_size=chunk_size)
        elif source_path.is_dir():
            if dest_path.is_file():
                dest_path.unlink()

            dest_path.mkdir(mode=0o755, parents=True, exist_ok=True)
            copydir(source_path, dest_path, chunk_size=chunk_size)


def strip_files(directory: Path, manifest: frozenset):
    """Removes all files from the directory tree,
    whose SHA-256 checksums are not in the manifest.
    """

    for path in get_files(directory):
        relpath = path.relative_to(directory)

        if str(relpath) not in manifest:
            LOGGER.debug('Removing obsolete file: %s.', path)
            path.unlink()


def strip_tree(directory: Path):
    """Removes all empty directory sub-trees."""

    def strip_subdir(subdir: Path):
        """Recursively removes empty directory trees."""
        for inode in subdir.iterdir():
            if inode.is_dir():
                strip_subdir(inode)

        if not tuple(subdir.iterdir()):     # Directory is empty.
            LOGGER.debug('Removing empty directory: %s.', subdir)
            subdir.rmdir()

    for inode in directory.iterdir():
        if inode.is_dir():
            strip_subdir(inode)


def load_manifest(tmpd: Path) -> frozenset:
    """Reads the manifest from the respective temporary directory."""

    LOGGER.debug('Reading manifest.')
    path = tmpd.joinpath(MANIFEST_FILENAME)

    with path.open('r') as file:
        manifest = load(file)

    path.unlink()   # File is no longer needed.
    return frozenset(manifest)


def get_directory(directory: str) -> Path:
    """Returns the target directory."""

    if directory == '.':
        return Path.cwd()

    return Path(directory)


def gen_manifest(directory: Path, chunk_size: int = 4096) -> Iterable[tuple]:
    """Yields the SHA-256 sums in the current working directory."""

    for filename in get_files(directory):
        sha256sum = sha256()

        with filename.open('rb') as file:
            for chunk in iter(partial(file.read, chunk_size), b''):
                sha256sum.update(chunk)

        sha256sum = sha256sum.hexdigest()
        LOGGER.debug('SHA-256 sum of "%s" is %s.', filename, sha256sum)
        relpath = filename.relative_to(directory)
        yield (str(relpath), sha256sum)


def update(directory: Path, file: BinaryIO, *, chunk_size: int = 4096) -> bool:
    """Updates the digital signage data
    from the respective tar.xz archive.
    """

    with TemporaryDirectory() as tmpd:
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
    return True


def server(socket: tuple):
    """Runs the HTTP server."""

    httpd = HTTPServer(socket, HTTPRequestHandler)
    LOGGER.info('Listening on %s:%i.', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 1

    return 0


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
        '-d', '--directory', type=Path, metavar='dir',
        default=Path.cwd(), help='sets the target directory')
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
    LOGGER.debug('Target directory set to: %s', args.directory)

    if not args.directory.is_dir():
        LOGGER.critical('Target directory does not exist: %s.', args.directory)
        return 2

    socket = (args.address, args.port)
    RUNTIME.update({
        'update': partial(update, args.direcory, chunk_size=args.chunk_size),
        'gen_manifest': partial(
            gen_manifest, args.direcory, chunk_size=args.chunk_size)})
    return server(socket)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    @staticmethod
    def update(file):
        """Performs update."""
        return RUNTIME['update'](file)

    @staticmethod
    def gen_manifest():
        """Returns the current manifest."""
        return dict(RUNTIME['gen_manifest']())

    @property
    def content_length(self) -> int:
        """Returns the content length."""
        return int(self.headers['Content-Length'])

    def send_data(self, value, status_code):
        """Sends the respective data."""
        if isinstance(value, (dict, list)):
            value = dumps(value)
            content_type = 'application/json'
        elif isinstance(value, str):
            content_type = 'text/plain'

        with suppress(AttributeError):
            body = value.encode()

        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):   # pylint: disable=C0103
        """Returns the manifest."""
        self.send_data(dict(self.gen_manifest()), 200)

    def do_POST(self):  # pylint: disable=C0103
        """Retrieves and updates digital signage data."""
        try:
            with LOCK_FILE:
                success = self.update(self.rfile)
        except Locked:
            self.send_data('Synchronization already in progress.', 503)
        else:
            self.send_data(dict(self.gen_manifest()), 200 if success else 500)


class LockFile:
    """Represents a lock file to lock synchronization."""

    def __init__(self, filename):
        """Sets the filename."""
        self.filename = filename

    def __enter__(self):
        """Creates the lock file."""
        self.create()
        return self

    def __exit__(self, *_):
        """Removes the lock file."""
        self.unlink()

    @property
    def basedir(self) -> Path:
        """Returns the base directory."""
        return Path(gettempdir())

    @property
    def path(self) -> Path:
        """Returns the file path."""
        return self.basedir.joinpath(self.filename)

    @property
    def exists(self) -> bool:
        """Tests whether the lock file exists."""
        return self.path.is_file()

    def create(self, content=b''):
        """Creates the lock file."""
        if self.exists:
            raise Locked()

        with self.path.open('wb') as file:
            file.write(content)

    def unlink(self):
        """Removes the lock file."""
        with suppress(FileNotFoundError):
            self.path.unlink()


LOCK_FILE = LockFile(LOCKFILE_NAME)


if __name__ == '__main__':
    exit(main())
