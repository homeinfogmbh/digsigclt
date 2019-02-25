#! /usr/bin/env python3
"""Digital signage cross-platform client."""

from argparse import ArgumentParser
from contextlib import suppress
from hashlib import sha256
from http.client import IncompleteRead
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from json import dumps, load, loads
from logging import DEBUG, INFO, basicConfig, getLogger
from pathlib import Path
from platform import architecture, machine, system
from socket import gethostname
from tarfile import open as tar_open
from tempfile import gettempdir, TemporaryDirectory
from threading import Thread
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, ParseResult
from urllib.request import urlopen, Request


DESCRIPTION = '''HOMEINFO multi-platform digital signage client.
Synchronizes data to the current working directory
or listens on the specified port when in server mode
to be triggered to do so.'''
SERVER = ('http', '10.8.0.1', '/appcmd/digsig')
MAX_RETRIES = 3
REG_KEY = r'SOFTWARE\HOMEINFO\digsigclt'
OS64BIT = {'AMD64', 'x86_64'}
LOCKFILE_NAME = 'digsigclt.sync.lock'
MANIFEST_FILENAME = 'manifest.json'
DEFAULT_DIR_LINUX = '/usr/share/digsig'
DEFAULT_DIR_WINDOWS = 'C:\\HOMEINFOGmbH\\content'
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


class MissingConfiguration(Exception):
    """Indicates that the configuration is missing."""


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
            LOGGER.debug('Updating: %s.', dest_path)

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
        with path.open('rb') as file:
            bytes_ = file.read()

        sha256sum = sha256(bytes_).hexdigest()

        if sha256sum not in manifest:
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


def read_manifest(tmpd):
    """Reads the manifest from the respective temporary directory."""

    LOGGER.debug('Reading manifest.')
    path = tmpd.joinpath(MANIFEST_FILENAME)

    with path.open('r') as file:
        manifest = load(file)

    path.unlink()   # File is no longer needed.
    return manifest


def get_directory(directory):
    """Returns the target directory."""

    if directory == '--':
        return Path.cwd()

    return Path(directory)


def get_default_directory():
    """Returns the target directory."""

    sys = system()

    if sys == 'Linux':
        return DEFAULT_DIR_LINUX

    if sys == 'Windows':
        return DEFAULT_DIR_WINDOWS

    raise UnsupportedSystem(sys)


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
    """Returns the configuration from the windows registry."""
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


def get_config():
    """Returns the respective configuration:"""

    sys = system()
    LOGGER.debug('Running on %s.', sys)

    if sys == 'Linux':
        return _get_config_linux()

    if sys == 'Windows':
        return _get_config_windows()

    raise UnsupportedSystem(sys)


def get_sha256sums(directory):
    """Yields the SHA-256 sums in the current working directory."""

    for filename in get_files(directory):
        with filename.open('rb') as file:
            bytes_ = file.read()

        sha256sum = sha256(bytes_).hexdigest()
        LOGGER.debug('Found file: %s (%s).', filename, sha256sum)
        yield sha256sum


def get_manifest(directory):
    """Returns the manifest list."""

    LOGGER.debug('Creating manifest of current files.')
    sha256sums = list(get_sha256sums(directory))
    return dumps(sha256sums)


def process_response(response):
    """Processes the response from the webserver."""

    if response.status == 200:
        content_type = response.headers.get('Content-Type')

        if content_type == 'application/x-xz':
            return response.read()

        raise InvalidContentType(content_type)

    raise ConnectionError(response.status)


def retrieve(directory, retries=0):
    """Retrieves data from the server."""

    config = get_config()
    params = {key: str(value) for key, value in config.items()}
    parse_result = ParseResult(*SERVER, '', urlencode(params), '')
    url = parse_result.geturl()
    data = get_manifest(directory).encode()
    headers = {'Content-Type': 'application/json'}
    request = Request(url, data=data, headers=headers)
    LOGGER.debug('Retrieving files from %s://%s%s.', *SERVER)

    with urlopen(request) as response:
        try:
            return process_response(response)
        except IncompleteRead:
            LOGGER.error('Could not read response from webserver.')

            if retries <= MAX_RETRIES:
                return retrieve(directory, retries=retries+1)

            raise


def update(tar_xz, directory):
    """Updates the digital signage data
    from the respective tar.xz archive.
    """

    fileobj = BytesIO(tar_xz)

    with TemporaryDirectory() as tmpd:
        with tar_open(mode='r:xz', fileobj=fileobj) as tar:
            tar.extractall(path=tmpd)

        tmpd = Path(tmpd)
        manifest = read_manifest(tmpd)
        copydir(tmpd, directory)

    strip_files(directory, manifest)
    strip_tree(directory)


def do_sync(directory):
    """Synchronizes the data."""

    try:
        tar_xz = retrieve(directory)
    except MissingConfiguration:
        LOGGER.critical('Cannot download data due to missing configuration.')
    except HTTPError as http_error:
        if http_error.code == 304:  # Data unchanged.
            LOGGER.info('Data unchanged.')
            return True

        LOGGER.critical('Could not download data: %s.', http_error)
    except URLError as url_error:
        LOGGER.critical('Could not download data: %s.', url_error)
    except IncompleteRead:
        LOGGER.critical('Could not retrieve data.')
    except ConnectionError as connection_error:
        LOGGER.critical('Connection error: %s.', connection_error)
    except InvalidContentType as invalid_content_type:
        LOGGER.critical(
            'Retrieved invalid content type: %s.',
            invalid_content_type.content_type)
    else:
        return update(tar_xz, directory)

    return False


def sync(directory):
    """Performs a data synchronization."""

    try:
        with LOCK_FILE:
            return do_sync(directory)
    except Locked:
        LOGGER.error('Synchronization is locked.')
        return False


def sync_in_thread(directory):
    """Starts the synchronization within a thread."""

    try:
        do_sync(directory)
    finally:
        LOCK_FILE.unlink()
        HTTPRequestHandler.sync_thread = None   # Reset thread.


def server(args):
    """Runs the HTTP server."""

    socket = ('localhost', args.port)
    HTTPRequestHandler.directory = args.directory
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
        '--port', '-p', type=int, default=5000, help='port to listen on')
    parser.add_argument(
        '--directory', '-d', type=get_directory,
        default=get_default_directory(), help='sets the target directory')
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='turn on verbose logging')
    args = parser.parse_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    LOGGER.debug('Target directory: %s', args.directory)

    if args.server:
        server(args)
    else:
        sync(args.directory)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests."""

    directory = None
    sync_thread = None

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

    def start_sync(self):
        """Starts a synchronization."""
        try:
            LOCK_FILE.create()    # Check lock file.
        except Locked:
            return False

        cls = type(self)

        if cls.sync_thread is None:
            cls.sync_thread = Thread(
                target=sync_in_thread, args=(self.directory,))
            cls.sync_thread.start()
            return True

        return False

    def do_POST(self):  # pylint: disable=C0103
        """Handles POST requests."""
        if self.json.get('command') == 'sync':
            if self.start_sync():
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
        response = BytesIO()
        response.write(body)
        self.wfile.write(response.getvalue())


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
    main()
