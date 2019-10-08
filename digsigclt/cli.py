"""Command line interface."""

from argparse import ArgumentParser
from ipaddress import IPv4Network
from logging import DEBUG, INFO, basicConfig
from pathlib import Path
from sys import exit    # pylint: disable=W0622

from digsigclt.common import CHUNK_SIZE, LOG_FORMAT, LOGGER
from digsigclt.exceptions import NetworkError
from digsigclt.network import get_address
from digsigclt.server import spawn


__all__ = ['main']


DESCRIPTION = 'HOMEINFO cross-platform digital signage client.'
DEFAULT_NETWORK = IPv4Network('10.8.0.0/16')


def get_args():
    """Returns the command line arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-a', '--address', metavar='address',
        help='IPv4 address to listen on')
    parser.add_argument(
        '-p', '--port', type=int, default=8000, metavar='port',
        help='port to listen on')
    parser.add_argument(
        '-n', '--network', type=IPv4Network, default=DEFAULT_NETWORK,
        metavar='network', help='network to search IP address on')
    parser.add_argument(
        '-d', '--directory', type=Path, metavar='dir', default=Path.cwd(),
        help='sets the target directory')
    parser.add_argument(
        '-c', '--chunk-size', type=int, default=CHUNK_SIZE, metavar='bytes',
        help='chunk size to use on file operations')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='turn on verbose logging')
    return parser.parse_args()


def main():
    """Main method to run."""

    args = get_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    LOGGER.debug('Target directory set to "%s".', args.directory)
    address = args.address

    if address is None:
        try:
            address = get_address(args.network)
        except NetworkError as network_error:
            LOGGER.critical(network_error)
            exit(2)

    if args.directory.is_dir():
        socket = (str(address), args.port)
        spawn(socket, args.directory, args.chunk_size)
        exit(0)

    LOGGER.critical('Target directory "%s" does not exist.', args.directory)
    exit(3)
