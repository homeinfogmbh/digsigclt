"""Command line interface."""

from argparse import ArgumentParser, Namespace
from ipaddress import ip_address
from logging import DEBUG, INFO, basicConfig
from pathlib import Path

from digsigclt.common import CHUNK_SIZE, LOG_FORMAT, LOGGER
from digsigclt.exceptions import NoAddressFound
from digsigclt.network import discover_address
from digsigclt.server import spawn
from digsigclt.types import Socket


__all__ = ["main"]


DESCRIPTION = "HOMEINFO cross-platform digital signage client."


def get_args() -> Namespace:
    """Returns the command line arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-a",
        "--address",
        metavar="address",
        type=ip_address,
        help="IP address to listen on",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, metavar="port", help="port to listen on"
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        metavar="dir",
        default=Path.cwd(),
        help="sets the target directory",
    )
    parser.add_argument(
        "-c",
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        metavar="bytes",
        help="chunk size to use on file operations",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="turn on verbose logging"
    )
    return parser.parse_args()


def main() -> int:
    """Main method to run."""

    args = get_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    LOGGER.debug('Target directory set to "%s".', args.directory)

    try:
        address = discover_address()
    except NoAddressFound:
        LOGGER.critical("No private network address found.")
        return 2

    if args.directory.is_dir():
        return spawn(Socket(address, args.port), args.directory, args.chunk_size)

    LOGGER.critical('Target directory "%s" does not exist.', args.directory)
    return 3
