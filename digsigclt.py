#! /usr/bin/env python3
"""Digital signage cross-platform client."""

from argparse import ArgumentParser
from contextlib import suppress
from hashlib import sha256
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from json import dumps, loads
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from platform import architecture, machine, system
from tarfile import open as tar_open
from tempfile import TemporaryDirectory
from urllib.parse import urlencode, ParseResult
from urllib.request import urlopen


DESCRIPTION = 'HOMEINFO multi-platform digital signage client.'
SERVER = ('http', '10.8.0.1', '/appcmd/digsig')
LOCKFILE_NAME = 'digsigclt.sync.lock'
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger('digsigclt')
REG_KEY = r'SOFTWARE\HOMEINFO\digsigclt'
OS64BIT = ('AMD64', 'x86_64')


class UnsupportedSystem(Exception):
    """Indicates that this script is running
    on an unsupported operating system.
    """

    def __init__(self, system):     # pylint: disable=W0621
        """Sets the operating system."""
        super().__init__()
        self.system = system


class MissingConfiguration(Exception):
    """Indicates that the configuration is missing."""


class DataUnchanged(Exception):
    """Indicates that there is no change to the digital signage data."""


class InvalidContentType(Exception):
    """Indicates that an invalid content type was received."""

    def __init__(self, content_type):
        """Sets the content type."""
        super().__init__()
        self.content_type = content_type


class Locked(Exception):
    """Indicates that the synchronization is currently locked."""


def is32on64():
    """Determines whether we run 32 bit
    python on a 64 bit oeprating system.
    """

    py_arch, _ = architecture()
    sys_arch = machine()
    return py_arch == '32bit' and sys_arch in OS64BIT


def copydir(source_dir, dest_dir):
    """Copies all contents of source_dir
    into dest_dir, overwriting all files.
    """
    for source_path in source_dir.iterdir():
        relpath = source_path.relative_to(source_dir)
        dest_path = dest_dir.joinpath(relpath)

        if source_path.is_file():
            with dest_path.path.open('wb') as dst:
                with source_path.open('rb') as src:
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

    for inode in directory.iterdir():
        if inode.is_file():
            with inode.open('rb') as file:
                bytes_ = file.read()

            sha256sum = sha256(bytes_).hexdigest()

            if sha256sum not in manifest:
                LOGGER.info('Removing obsolete file: %s.', inode)
                inode.unlink()


def strip_tree(directory):
    """Removes all empty directory sub-trees."""

    def strip_subdir(subdir):
        """Recursively removes empty directory trees."""
        for inode in subdir.iterdir():
            if inode.is_dir():
                strip_subdir(inode)

        if not tuple(subdir.iterdir()):     # Directory is empty.
            subdir.rmdir()

    for inode in directory.iterdir():
        if inode.is_dir():
            strip_subdir(inode)


def _get_config_linux():
    """Returns the configuration on a Linux system."""

    try:
        with open('/etc/hostname', 'r') as file:
            hostname = file.read()
    except FileNotFoundError:
        LOGGER.error('/etc/hostname does not exist.')
        raise MissingConfiguration()
    except PermissionError:
        LOGGER.error('Cannot read /etc/hostname. Insufficient permissions.')
        raise MissingConfiguration()

    hostname = hostname.strip()

    try:
        tid, cid = hostname.split('.')
    except ValueError:
        try:
            return {'id': int(hostname)}    # For future global terminal IDs.
        except ValueError:
            LOGGER.error('No valid configuration found in /etc/hostname.')
            raise MissingConfiguration()

    return {'tid': int(tid), 'cid': int(cid)}


def _get_config_windows():
    """Returns the configuration from the windows registry."""
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

    if not configuration:
        raise MissingConfiguration()


def get_config():
    """Returns the respective configuration:"""

    sys = system()

    if sys == 'Linux':
        return _get_config_linux()

    if sys == 'Windows':
        return _get_config_windows()

    raise UnsupportedSystem(sys)


def retrieve():
    """Retrieves data from the server."""

    config = get_config()
    params = {key: str(value) for key, value in config.items()}
    parse_result = ParseResult(*SERVER, '', urlencode(params), '')
    url = parse_result.geturl()

    with urlopen(url) as response:
        if response.status == 304:
            raise DataUnchanged()

        if response.status == 200:
            content_type = response.headers.get('Content-Type')

            if content_type == 'application/x-xz':
                return response.read()

            raise InvalidContentType(content_type)

        raise ConnectionError(response.status)


def update(tar_xz, directory):
    """Updates the digital signage data
    from the respective tar.xz archive.
    """

    fileobj = BytesIO(tar_xz)

    with TemporaryDirectory() as tmpd:
        with tar_open(mode='r:xz', fileobj=fileobj) as tar:
            tar.extractall(path=tmpd)

        copydir(Path(tmpd), directory)


def do_sync(args):
    """Synchronizes the data."""

    try:
        tar_xz = retrieve()
    except MissingConfiguration:
        LOGGER.error('Cannot download data due to missing configuration.')
        return False
    except DataUnchanged:
        return True
    except ConnectionError as connection_error:
        LOGGER.error('Connection error: %s.', connection_error)
        return False
    except InvalidContentType as invalid_content_type:
        LOGGER.error(
            'Retrieved invalid content type: %s.',
            invalid_content_type.content_type)
        return False

    return update(tar_xz, args.directory)


def sync(args):
    """Performs a data synchronization."""

    try:
        with LockFile(LOCKFILE_NAME):
            return do_sync(args)
    except Locked:
        LOGGER.error('Synchronization is locked.')
        return False


def trigger_sync():
    """Triggers the synchronization."""

    try:
        raise NotADirectoryError()
    except Locked:
        status_code = 503
        message = 'Sync locked.'
    else:
        status_code = 200
        message = 'Synchronization triggered.'

    return ({'message': message}, status_code)


def server(args):
    """Runs the HTTP server."""

    socket = ('localhost', args.port)
    httpd = HTTPServer(socket, HTTPRequestHandler)
    LOGGER.info('Listening on %s:%i.', *socket)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return


def main():
    """Main method to run."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '--server', '-S', action='store_true', help='run in server mode')
    parser.add_argument(
        '--port', '-p', type=int, default=5000, help='port to listen on')
    parser.add_argument(
        '--directory', '-d', type=Path, default=Path.cwd(),
        help='base directory')
    args = parser.parse_args()
    basicConfig(level=INFO, format=LOG_FORMAT)

    if args.server:
        server(args)
    else:
        sync(args)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests."""

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

    @property
    def command(self):
        """Returns the sent JSON command."""
        return self.json.get('command')

    def do_POST(self):  # pylint: disable=C0103
        """Handles POST requests."""
        if self.command == 'sync':
            json, status_code = trigger_sync()
        else:
            json = {'message': 'Invalid command.'}
            status_code = 400

        body = dumps(json).encode()
        self.send_response(status_code)
        self.end_headers()
        response = BytesIO()
        response.write(body)
        self.wfile.write(response.getvalue())


class LockFile:
    """Represents a lock file to lock synchronization."""

    def __init__(self, filename):
        """Sets the filename."""
        self.filename = filename
        self._basedir_linux = Path('/tmp')
        self._basedir_windows = NotImplemented

    def __enter__(self):
        """Creates the lock file."""
        self.create()
        return self

    def __exit__(self, *_):
        """Removes the lock file."""
        self.unlink()

    @property
    def basedir(self):
        """Returns the base path."""
        sys = system()

        if sys == 'Linux':
            return self._basedir_linux

        if sys == 'Windows':
            return self._basedir_windows

        raise UnsupportedSystem(sys)

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


if __name__ == '__main__':
    main()
