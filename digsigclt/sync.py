"""Digital signage data synchronization."""

from contextlib import suppress
from functools import partial
from hashlib import sha256
from json import loads
from pathlib import Path
from tarfile import ReadError, open as tar_open
from tempfile import TemporaryDirectory
from traceback import format_exc

from digsigclt.common import CHUNK_SIZE, LOGFILE, LOGGER
from digsigclt.exceptions import ManifestError


__all__ = ['gen_manifest', 'update']


def get_files(directory):
    """Recursively lists files in the given
    directory, excluding the LOGFILE.
    """

    for inode in directory.iterdir():
        if inode.is_dir():
            yield from get_files(inode)
        elif inode.is_file() and inode.relative_to(directory) != LOGFILE:
            yield inode


def copy_file(src, dst, *, chunk_size=CHUNK_SIZE):
    """Copies a file from src to dst."""

    with src.open('rb') as src_file, dst.open('wb') as dst_file:
        for chunk in iter(partial(src_file.read, chunk_size), b''):
            dst_file.write(chunk)


def copy_directory(src, dst, *, chunk_size=CHUNK_SIZE):
    """Copies all contents of the source directory src
    into the destination directory dst, overwriting all files.
    """

    LOGGER.debug('Copying "%s" to "%s".', src, dst)

    for source_path in src.iterdir():
        relpath = source_path.relative_to(src)
        dest_path = dst.joinpath(relpath)

        if source_path.is_file():
            LOGGER.info('Updating file "%s".', dest_path)
            copy_file(source_path, dest_path, chunk_size=chunk_size)
        elif source_path.is_dir():
            if dest_path.is_file():
                dest_path.unlink()

            if not dest_path.is_dir():
                dest_path.mkdir(mode=0o755, parents=True)

            copy_directory(source_path, dest_path, chunk_size=chunk_size)
        else:
            LOGGER.warning('Skipping unknown file: "%s".', source_path)


def strip_files(directory, manifest):
    """Removes all files from the directory
    tree, which are not in the manifest.
    """

    for path in get_files(directory):
        relpath = path.relative_to(directory)

        if relpath not in manifest:
            LOGGER.debug('Removing obsolete file "%s".', path)

            try:
                path.unlink()
            except FileNotFoundError:
                LOGGER.warning('File "%s" vanished.', path)
            except PermissionError:
                LOGGER.error('Could not delete file "%s".', path)


def strip_tree(directory):
    """Removes all empty directory sub-trees."""

    def strip_subdir(subdir):
        """Recursively removes empty directory trees."""
        for inode in subdir.iterdir():
            if inode.is_dir():
                strip_subdir(inode)

        if not set(subdir.iterdir()):   # Directory is probably empty.
            with suppress(OSError):
                subdir.rmdir()
                LOGGER.debug('Removed empty directory "%s".', subdir)

    for inode in directory.iterdir():
        if inode.is_dir():
            strip_subdir(inode)


def load_manifest(directory):
    """Reads the manifest from the respective directory."""

    path = directory.joinpath('manifest.json')
    LOGGER.debug('Reading manifest from "%s".', path)

    try:
        with path.open('r') as file:
            text = file.read()
    except FileNotFoundError:
        LOGGER.error('Manifest not found: "%s".', path)
        raise ManifestError()

    try:
        manifest = loads(text)
    except ValueError:
        LOGGER.error('Manifest is not valid JSON: "%s".', path)
        LOGGER.debug(text)
        raise ManifestError()

    if not isinstance(manifest, list):
        LOGGER.error('Manifest is not a list: "%s".', path)
        LOGGER.debug(type(manifest))
        LOGGER.debug(manifest)
        raise ManifestError()

    # Remove file to prevent it from being copied
    # to the digital signage data directory.
    path.unlink()
    return {Path(*parts) for parts in manifest}


def gen_manifest(directory, *, chunk_size=CHUNK_SIZE):
    """Generates the manifest of relative
    file paths and their SHA-256 checksums.
    """

    manifest = {}

    for filename in get_files(directory):
        sha256sum = sha256()

        with filename.open('rb') as file:
            for chunk in iter(partial(file.read, chunk_size), b''):
                sha256sum.update(chunk)

        sha256sum = sha256sum.hexdigest()
        LOGGER.debug('SHA-256 sum of "%s" is "%s".', filename, sha256sum)
        relpath = filename.relative_to(directory)
        manifest[relpath.parts] = sha256sum

    return list(manifest.items())   # Need list for JSON serialization.


def update(file, directory, *, chunk_size=CHUNK_SIZE):
    """Updates the digital signage data
    from the respective tar.xz archive.
    """

    with TemporaryDirectory() as tmpd:
        LOGGER.debug('Extracting archive to "%s".', tmpd)

        with tar_open(mode='r:xz', fileobj=file, bufsize=chunk_size) as tar:
            try:
                tar.extractall(path=tmpd)
            except EOFError as eof_error:
                LOGGER.critical(eof_error)
                return False
            except ReadError as read_error:
                LOGGER.critical(read_error)
                return False

        tmpd = Path(tmpd)

        try:
            manifest = load_manifest(tmpd)
        except ManifestError:
            return False

        try:
            copy_directory(tmpd, directory, chunk_size=chunk_size)
        except PermissionError as permission_error:
            LOGGER.error(permission_error)
            LOGGER.debug(format_exc())
            return False

    strip_files(directory, manifest)
    strip_tree(directory)
    return True
