"""Updating process for Windows systems."""

from contextlib import suppress
from json import dumps
from os import execv, name, rename
from pathlib import Path
from sys import argv, executable
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from digsigclt.common import LOGGER
from digsigclt.exceptions import NoUpdateAvailable
from digsigclt.exceptions import RunningOldExe
from digsigclt.exceptions import UpdateProtocolError
from digsigclt.functions import fileinfo


__all__ = ['UPDATE_URL', 'update']


APPCMD = 'http://appcmd.homeinfo.intra/appcmd/'
OLD_NAME = 'digsigclt_old.exe'
UPDATE_URL = urljoin(APPCMD, 'update/digsigclt')


def get_old_path() -> Path:
    """Returns the path for the older,
    to-be deleted Windows executable.
    """

    if (exe := Path(executable)).name == OLD_NAME:
        raise RunningOldExe()

    return exe.parent.joinpath(OLD_NAME)


def retrieve_update(url: str) -> bytes:
    """Retrieves a new version of the exe."""

    request = Request(url)
    request.add_header('Content-Type', 'application/json')
    json = dumps(fileinfo(executable))

    with urlopen(request, data=json) as response:
        if response.code == 204:
            raise NoUpdateAvailable()

        if response.code == 200:
            return response.read()

        raise UpdateProtocolError(response.code)


def update_exe(exe_file: bytes):
    """Updates the *.exe file."""

    LOGGER.debug('Removing old exe.')
    old_path = get_old_path()

    with suppress(FileNotFoundError):
        old_path.unlink()

    LOGGER.debug('Renaming current exe to old exe.')
    rename(executable, str(old_path))
    LOGGER.debug('Writing new exe file.')

    with open(executable, 'wb') as exe:
        exe.write(exe_file)
        exe.flush()


def update(url: str):
    """Updates the Windows executable and restarts it."""

    if name != 'nt':
        LOGGER.debug('Not running on Windows. Skipping update process.')
        return

    LOGGER.info('Checking for update.')

    try:
        exe_file = retrieve_update(url)
    except HTTPError as error:
        LOGGER.error('Could not query update server.')
        LOGGER.debug('Status: %i, reason: %s.', error.code, error.reason)
        return
    except URLError as error:
        LOGGER.error('Could not query update server.')
        LOGGER.debug('Reason: %s.', error.reason)
        return
    except UpdateProtocolError as error:
        LOGGER.error('Update protocol error.')
        LOGGER.debug('Server responded with status: %i.', error.code)
        return
    except NoUpdateAvailable:
        LOGGER.info('No update available.')
        return

    update_exe(exe_file)
    LOGGER.debug('Substituting running process with new executable.')
    execv(executable, argv)
