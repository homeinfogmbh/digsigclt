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

from argparse import ArgumentParser
from contextlib import suppress
from functools import lru_cache
from hashlib import sha256
from http.client import IncompleteRead
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from json import dumps, load, loads
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from platform import architecture, machine, system
from socket import gethostname
from sys import exit    # pylint: disable=W0622
from tarfile import open as tar_open
from tempfile import gettempdir, TemporaryDirectory
from threading import Thread
from urllib.error import URLError
from urllib.parse import urlencode, urlparse, ParseResult
from urllib.request import urlopen, Request


DESCRIPTION = '''HOMEINFO multi-platform digital signage client.
Synchronizes data to the current working directory
or listens on the specified port when in server mode
to be triggered to do so.'''
REG_KEY = r'SOFTWARE\HOMEINFO\digsigclt'
OS64BIT = {'AMD64', 'x86_64'}
LOCKFILE_NAME = 'digsigclt.sync.lock'
MANIFEST_FILENAME = 'manifest.json'
DEFAULT_DIRS = {
    'Linux': '/usr/share/digsig',
    'Windows': 'C:\\HOMEINFOGmbH\\content'}
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger('digsigclt')


class UnsupportedSystem(Exception):
    """Indicates that this script is running
    on an unsupported operating system.
    """

    def __init__(self, system):     # pylint: disable=W0621
        """Sets the operating system."""
        super().__init__()
        self.system = system

    def __str__(self):
        return self.system


class MissingConfiguration(Exception):
    """Indicates that the configuration is missing."""


class InvalidContentType(Exception):
    """Indicates that an invalid content type was received."""

    def __init__(self, content_type):
        """Sets the content type."""
        super().__init__()
        self.content_type = content_type

    def __str__(self):
        return str(self.content_type)


class Locked(Exception):
    """Indicates that the synchronization is currently locked."""


@lru_cache(maxsize=1)
def get_os():
    """Returns the operating system."""

    os_ = system()
    LOGGER.debug('Running on %s.', os_)
    return os_


def is32on64():
    """Determines whether we run 32 bit
    python on a 64 bit operating system.
    """

    py_arch, _ = architecture()
    sys_arch = machine()
    return py_arch == '32bit' and sys_arch in OS64BIT


def get_files(directory):
    """Lists the current files."""

    for inode in directory.iterdir():
        if inode.is_dir():
            yield from get_files(directory=inode)
        elif inode.is_file():
            yield inode


def copydir(source_dir, dest_dir):
    """Copies all contents of source_dir
    into dest_dir, overwriting all files.
    """

    for source_path in source_dir.iterdir():
        relpath = source_path.relative_to(source_dir)
        dest_path = dest_dir.joinpath(relpath)

        if source_path.is_file():
            LOGGER.info('Updating: %s.', dest_path)

            with dest_path.open('wb') as dst, source_path.open('rb') as src:
                dst.write(src.read())
        elif source_path.is_dir():
            if dest_path.is_file():
                dest_path.unlink()

            dest_path.mkdir(mode=0o755, parents=True, exist_ok=True)
            copydir(source_path, dest_path)


def strip_files(directory, manifest):
    """Removes all files from the directory tree,
    whose SHA-256 checksums are not in the manifest.
    """

    for path in get_files(directory):
        relpath = path.relative_to(directory)

        if str(relpath) not in manifest:
            LOGGER.debug('Removing obsolete file: %s.', path)
            path.unlink()


def strip_tree(directory):
    """Removes all empty directory sub-trees."""

    def strip_subdir(subdir):
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


def get_manifest(tmpd):
    """Reads the manifest from the respective temporary directory."""

    LOGGER.debug('Reading manifest.')
    path = tmpd.joinpath(MANIFEST_FILENAME)

    with path.open('r') as file:
        manifest = load(file)

    path.unlink()   # File is no longer needed.
    return frozenset(manifest)


def get_directory(directory):
    """Returns the target directory."""

    if directory == '.':
        return Path.cwd()

    return Path(directory)


def get_default_directory():
    """Returns the target directory."""

    try:
        return DEFAULT_DIRS[get_os()]
    except KeyError:
        raise UnsupportedSystem(get_os())


def _get_config_linux():
    """Returns the configuration on a Linux system."""

    hostname = gethostname()

    try:
        tid, cid = hostname.split('.')
    except ValueError:
        try:
            ident = int(hostname)   # For future global terminal IDs.
        except ValueError:
            LOGGER.error('No valid configuration found in /etc/hostname.')
            raise MissingConfiguration()

        return {'id': ident}

    try:
        tid = int(tid)
    except ValueError:
        LOGGER.error('TID is not an integer.')
        raise MissingConfiguration()

    try:
        cid = int(cid)
    except ValueError:
        LOGGER.error('CID is not an interger.')
        raise MissingConfiguration()

    return {'tid': tid, 'cid': cid}


def _get_config_windows():
    """Returns the configuration on a Windows system."""
    # Import winreg in Windows-specific function
    # since it is not available on non-Windows systems.
    from winreg import HKEY_LOCAL_MACHINE   # pylint: disable=E0401
    from winreg import KEY_READ             # pylint: disable=E0401
    from winreg import KEY_WOW64_64KEY      # pylint: disable=E0401
    from winreg import OpenKey              # pylint: disable=E0401
    from winreg import QueryValueEx         # pylint: disable=E0401

    def read_config(key):
        """Reads the configuration from the respective key."""
        for config_option in ('tid', 'cid', 'id'):
            try:
                value, type_ = QueryValueEx(key, config_option)
            except FileNotFoundError:
                LOGGER.warning('Key not found: %s.', config_option)
                continue

            if type_ != 1:
                message = 'Unexpected registry type %i for key "%s".'
                LOGGER.error(message, type_, config_option)
                continue

            try:
                value = int(value)
            except ValueError:
                message = 'Expected int value for key %s not "%s".'
                LOGGER.error(message, config_option, value)
                continue

            yield (config_option, value)

    access = KEY_READ

    if is32on64():
        access |= KEY_WOW64_64KEY

    try:
        with OpenKey(HKEY_LOCAL_MACHINE, REG_KEY, access=access) as key:
            configuration = dict(read_config(key))
    except FileNotFoundError:
        LOGGER.error('Registry key not set: %s.', REG_KEY)
        raise MissingConfiguration()

    if configuration:
        return configuration

    raise MissingConfiguration()


CONFIG_FUNCS = {
    'Linux': _get_config_linux,
    'Windows': _get_config_windows}


def get_config():
    """Returns the respective configuration:"""

    try:
        return CONFIG_FUNCS[get_os()]()
    except KeyError:
        raise UnsupportedSystem(get_os())


def get_sha256sums(directory):
    """Yields the SHA-256 sums in the current working directory."""

    for filename in get_files(directory):
        with filename.open('rb') as file:
            bytes_ = file.read()

        sha256sum = sha256(bytes_).hexdigest()
        LOGGER.debug('Found file: %s (%s).', filename, sha256sum)
        yield sha256sum


def get_sha256list(directory):
    """Returns the manifest list."""

    LOGGER.debug('Creating SHA-256 sums of current files.')
    sha256sums = list(get_sha256sums(directory))
    return dumps(sha256sums)


def read_retry(response, max_retries, *, retries=0):
    """Reads the respective response."""

    try:
        return response.read()
    except IncompleteRead:
        LOGGER.error('Could not read response from webserver.')

        if retries <= max_retries:
            return read_retry(response, max_retries, retries=retries+1)

        raise


def retrieve(config, args):
    """Retrieves data from the server."""

    scheme, netloc, path, params, _, fragment = args.url
    query = urlencode({key: str(value) for key, value in config.items()})
    url = ParseResult(scheme, netloc, path, params, query, fragment).geturl()
    headers = {'Content-Type': 'application/json'}
    sha256sums = get_sha256list(args.directory)
    request = Request(url, data=sha256sums.encode(), headers=headers)
    LOGGER.debug('Retrieving files from %s.', request.full_url)

    with urlopen(request) as response:
        content_type = response.headers.get('Content-Type')

        if content_type == 'application/x-xz':
            return read_retry(response, args.max_retries)

        raise InvalidContentType(content_type)


def update(tar_xz, directory):
    """Updates the digital signage data
    from the respective tar.xz archive.
    """

    fileobj = BytesIO(tar_xz)

    with TemporaryDirectory() as tmpd:
        with tar_open(mode='r:xz', fileobj=fileobj) as tar:
            tar.extractall(path=tmpd)

        tmpd = Path(tmpd)
        manifest = get_manifest(tmpd)

        try:
            copydir(tmpd, directory)
        except PermissionError as permission_error:
            LOGGER.critical(permission_error)
            return False

    strip_files(directory, manifest)
    strip_tree(directory)
    return True


def do_sync(config, args):
    """Synchronizes the data."""

    try:
        tar_xz = retrieve(config, args)
    except MissingConfiguration:
        LOGGER.critical('Cannot download data due to missing configuration.')
    except URLError as url_error:
        LOGGER.critical('Could not download data: %s.', url_error)
    except IncompleteRead as incomplete_read:
        LOGGER.critical('Could not read data: %s.', incomplete_read)
    except ConnectionError as connection_error:
        LOGGER.critical('Connection error: %s.', connection_error)
    except InvalidContentType as invalid_content_type:
        LOGGER.critical(
            'Received invalid content type: %s.', invalid_content_type)
    else:
        return update(tar_xz, args.directory)

    return False


def sync_in_thread(config, args):
    """Starts the synchronization within a thread."""

    try:
        do_sync(config, args)
    finally:
        LOCK_FILE.unlink()  # Release lock acquired outside of thread.


def sync(config, args):
    """Performs a data synchronization."""

    try:
        with LOCK_FILE:
            return do_sync(config, args)
    except Locked:
        LOGGER.error('Synchronization is locked.')
        return False


def server(config, args):
    """Runs the HTTP server."""

    socket = ('0.0.0.0', args.port)
    HTTPRequestHandler.args = (config, args)
    httpd = HTTPServer(socket, HTTPRequestHandler)
    LOGGER.info('Listening on %s:%i.', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        if HTTPRequestHandler.sync_thread is not None:
            HTTPRequestHandler.sync_thread.join()

        return


def main():
    """Main method to run."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '--server', '-S', action='store_true', help='run in server mode')
    parser.add_argument(
        '--url', '-u', type=urlparse, default='http://10.8.0.1/appcmd/digsig',
        help='the URL to the remote server')
    parser.add_argument(
        '--port', '-p', type=int, default=5000, help='port to listen on')
    parser.add_argument(
        '--directory', '-d', type=get_directory,
        default=get_default_directory(), help='sets the target directory')
    parser.add_argument(
        '--max-retries', '-r', type=int, default=3,
        help='maximum amount to retry HTTP connections')
    parser.add_argument(
        '--config', '-c', type=loads, default=None,
        help='use the specified config')
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='turn on verbose logging')
    args = parser.parse_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    LOGGER.debug('Target directory: %s', args.directory)

    if not args.directory.is_dir():
        LOGGER.critical('Target directory does not exist: %s.', args.directory)
        exit(2)

    if not args.config:
        try:
            config = get_config()
        except MissingConfiguration:
            LOGGER.critical('No configuration found.')
            exit(3)
    else:
        config = args.config

    if args.server:
        server(config, args)
    else:
        if sync(config, args):
            exit(0)
        else:
            exit(1)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    args = ()
    sync_thread = None

    @classmethod
    def sync_pending(cls):
        """Returns wehter a synchronization is currently pending."""
        if cls.sync_thread is None:
            return False

        if cls.sync_thread.is_alive():
            return True

        cls.sync_thread.join()  # Just to be on the safe side.
        return False

    @classmethod
    def start_sync(cls):
        """Starts a synchronization."""
        try:
            LOCK_FILE.create()  # Acquire lock.
        except Locked:
            return False

        if cls.sync_pending():
            LOCK_FILE.unlink()
            return False

        cls.sync_thread = Thread(target=sync_in_thread, args=cls.args)
        cls.sync_thread.start()
        return True

    @property
    def content_length(self):
        """Returns the content length."""
        return int(self.headers['Content-Length'])

    @property
    def bytes(self):
        """Returns the POSTed bytes."""
        return self.rfile.read(self.content_length)

    @property
    def json(self):
        """Returns POSTed JSON data."""
        return loads(self.bytes)

    def do_POST(self):  # pylint: disable=C0103
        """Handles POST requests."""
        LOGGER.debug('Received POST request.')

        if self.json.get('command') == 'sync':
            LOGGER.debug('Received sync command.')

            if type(self).start_sync():
                message = 'Synchronization started.'
                status_code = 202
            else:
                message = 'Synchronization already in progress.'
                status_code = 503
        else:
            message = 'Invalid command.'
            status_code = 400

        json = {'message': message}
        body = dumps(json).encode()
        self.send_response(status_code)
        self.end_headers()
        self.wfile.write(body)


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
    def basedir(self):
        """Returns the base directory."""
        return Path(gettempdir())

    @property
    def path(self):
        """Returns the file path."""
        return self.basedir.joinpath(self.filename)

    @property
    def exists(self):
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
    try:
        main()
    except UnsupportedSystem as unsupported_system:
        LOGGER.critical('Cannot run on %s.', unsupported_system)
        exit(4)
