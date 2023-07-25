"""Digital signage data synchronization."""

from hashlib import sha256
from json import loads
from pathlib import Path
from tarfile import ReadError, open as tar_open
from tempfile import TemporaryDirectory
from typing import IO, Iterable

from digsigclt.common import CHUNK_SIZE, LOGFILE, LOGGER
from digsigclt.exceptions import ManifestError
from digsigclt.types import Manifest


__all__ = ["gen_manifest", "update"]


MANIFEST = "manifest.json"


def get_files(directory: Path, *, basedir: bool = True) -> Iterable[Path]:
    """Recursively lists files in the given
    directory, excluding the LOGFILE.
    """

    for inode in directory.iterdir():
        if basedir and inode.stem.startswith("."):
            continue  # Ignore dotfiles in the base directory.

        if inode.is_dir():
            yield from get_files(inode, basedir=False)
        elif inode.is_file() and inode.relative_to(directory) != LOGFILE:
            yield inode


def get_orphans(directory: Path, manifest: set[Path]) -> Iterable[Path]:
    """Yields files within directory, that are not listed in manifest."""

    for path in get_files(directory):
        if path.relative_to(directory) not in manifest:
            yield path


def copy_file(src: Path, dst: Path, *, chunk_size: int = CHUNK_SIZE):
    """Copies a file from src to dst."""

    with src.open("rb") as src_file, dst.open("wb") as dst_file:
        while (chunk := src_file.read(chunk_size)) != b"":
            dst_file.write(chunk)


def copy_subfile(src: Path, dst: Path, *, chunk_size: int = CHUNK_SIZE):
    """Copies a sub-file."""

    LOGGER.info('Updating file "%s".', dst)

    try:
        copy_file(src, dst, chunk_size=chunk_size)
    except PermissionError:
        LOGGER.error("Could not override file: %s", dst)


def copy_subdir(src: Path, dst: Path, *, chunk_size: int = CHUNK_SIZE):
    """Copies a subdirectory."""

    if dst.is_file():
        try:
            dst.unlink()
        except PermissionError:
            LOGGER.error("Could not remove file: %s", dst)
            return

    if not dst.is_dir():
        dst.mkdir(mode=0o755, parents=True)

    copy_directory(src, dst, chunk_size=chunk_size)


def copy_directory(src: Path, dst: Path, *, chunk_size: int = CHUNK_SIZE):
    """Copies all contents of the source directory src
    into the destination directory dst, overwriting all files.
    """

    LOGGER.debug("%s -> %s", src, dst)

    for src_path in src.iterdir():
        relpath = src_path.relative_to(src)
        dst_path = dst / relpath

        if src_path.is_file():
            copy_subfile(src_path, dst_path, chunk_size=chunk_size)
        elif src_path.is_dir():
            copy_subdir(src_path, dst_path, chunk_size=chunk_size)
        else:
            LOGGER.warning("Skipping unknown file: %s", src_path)


def strip_files(directory: Path, manifest: set[Path]):
    """Removes all files from the directory
    tree, which are not in the manifest.
    """

    for path in get_orphans(directory, manifest):
        LOGGER.debug("Removing obsolete file: %s", path)

        try:
            path.unlink()
        except FileNotFoundError:
            LOGGER.warning("File vanished: %s", path)
        except PermissionError:
            LOGGER.error("Could not delete file: %s", path)


def strip_tree(directory: Path, *, basedir: bool = True):
    """Remove all empty directory subtrees."""

    for inode in directory.iterdir():
        if basedir and inode.stem.startswith("."):
            continue  # Do not remove dotfiles in the base directory.

        if inode.is_dir():
            strip_tree(inode, basedir=False)

    if basedir or any(directory.iterdir()):
        return  # Do not attempt to remove base directory or non-empty dirs.

    try:
        directory.rmdir()
    except OSError:
        LOGGER.warning("Could not remove directory: %s", directory)
    else:
        LOGGER.debug("Removed empty directory: %s", directory)


def load_manifest(directory: Path) -> set[Path]:
    """Read the manifest from the respective directory."""

    path = directory / MANIFEST
    LOGGER.debug("Reading manifest from: %s", path)

    try:
        with path.open("r") as file:
            text = file.read()
    except FileNotFoundError:
        LOGGER.error("Manifest not found: %s", path)
        raise ManifestError() from None

    try:
        manifest = loads(text)
    except ValueError:
        LOGGER.error("Manifest is not valid JSON: %s", path)
        LOGGER.debug(text)
        raise ManifestError() from None

    if not isinstance(manifest, list):
        LOGGER.error("Manifest is not a list: %s", path)
        LOGGER.debug(type(manifest))
        LOGGER.debug(manifest)
        raise ManifestError()

    # Remove file to prevent it from being copied
    # to the digital signage data directory.
    path.unlink()
    return {Path(*parts) for parts in manifest}


def gen_manifest(directory: Path, *, chunk_size: int = CHUNK_SIZE) -> Manifest:
    """Generate the manifest of relative
    file paths and their SHA-256 checksums.
    """

    for filename in get_files(directory):
        sha256sum = sha256()

        with filename.open("rb") as file:
            while (chunk := file.read(chunk_size)) != b"":
                sha256sum.update(chunk)

        sha256sum = sha256sum.hexdigest()
        LOGGER.debug("%s  %s", sha256sum, filename)
        relpath = filename.relative_to(directory)
        yield relpath.parts, sha256sum


def update(file: IO, directory: Path, *, chunk_size: int = CHUNK_SIZE) -> bool:
    """Update the digital signage data
    from the respective tar.xz archive.
    """

    with TemporaryDirectory() as temp_dir:
        LOGGER.debug("Extracting archive to: %s", temp_dir := Path(temp_dir))

        with tar_open(mode="r:xz", fileobj=file, bufsize=chunk_size) as tar:
            try:
                tar.extractall(path=temp_dir)
            except EOFError as eof_error:
                LOGGER.critical(eof_error)
                return False
            except ReadError as read_error:
                LOGGER.critical(read_error)
                return False

        try:
            manifest = load_manifest(temp_dir)
        except ManifestError:
            return False

        try:
            copy_directory(temp_dir, directory, chunk_size=chunk_size)
        except PermissionError as permission_error:
            LOGGER.error(permission_error)
            return False

    strip_files(directory, manifest)
    strip_tree(directory)
    return True
