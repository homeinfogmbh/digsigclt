"""Command line interface."""

from argparse import ArgumentParser
from ipaddress import ip_address, IPv4Address
from logging import DEBUG, INFO, basicConfig
from pathlib import Path
from sys import exit    # pylint: disable=W0622

from digsigclt.common import CHUNK_SIZE, LOG_FORMAT, LOGGER
from digsigclt.exceptions import RunningOldExe
from digsigclt.server import spawn
from digsigclt.update import UPDATE_URL, update


__all__ = ['main']


DESCRIPTION = 'HOMEINFO cross-platform digital signage client.'
DEFAULT_ADDRESS = IPv4Address('0.0.0.0')


def get_args():
    """Returns the command line arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-a', '--address', type=ip_address, default=DEFAULT_ADDRESS,
        metavar='address', help='IPv4 address to listen on')
    parser.add_argument(
        '-p', '--port', type=int, default=8000, metavar='port',
        help='port to listen on')
    parser.add_argument(
        '-d', '--directory', type=Path, metavar='dir', default=Path.cwd(),
        help='sets the target directory')
    parser.add_argument(
        '-s', '--update-server', metavar='url', default=UPDATE_URL,
        help='URL of the update server')
    parser.add_argument(
        '-c', '--chunk-size', type=int, default=CHUNK_SIZE, metavar='bytes',
        help='chunk size to use on file operations')
    parser.add_argument(
        '-i', '--interval', type=int, default=1, metavar='seconds',
        help='interval to wait for network address discovery')
    parser.add_argument(
        '-r', '--retries', type=int, default=60, metavar='amount',
        help='amount of retries of network address discovery')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='turn on verbose logging')
    return parser.parse_args()


def main():
    """Main method to run."""

    args = get_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    LOGGER.debug('Target directory set to "%s".', args.directory)

    try:
        update(args.update_server)
    except RunningOldExe:
        LOGGER.critical('Refusing to run old exe version.')
        exit(5)

    if args.directory.is_dir():
        socket = (str(args.address), args.port)
        spawn(socket, args.directory, args.chunk_size)
        exit(4)

    LOGGER.critical('Target directory "%s" does not exist.', args.directory)
    exit(3)
