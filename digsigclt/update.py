"""Updating process for Windows systems."""

from hashlib import sha256
from os import execl, name, rename
from pathlib import Path
from sys import argv, executable
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

from digsigclt.common import LOGGER
from digsigclt.exceptions import RunningOldExe, NoUpdateAvailable


__all__ = ['update']


EXECUTABLE = Path(executable)
OLD_NAME = 'digsigclt_old.exe'
UPDATE_URL = 'http://10.8.0.1/appcmd/digsigclt'


def get_old_path():
    """Returns the path for the older,
    to-be deleted Windows executable.
    """

    if EXECUTABLE.name == OLD_NAME:
        raise RunningOldExe()

    return EXECUTABLE.parent.joinpath(OLD_NAME)


def get_checksum():
    """Returns the checksum of the running digital signage client exe."""

    with open(executable, 'rb') as file:
        return sha256(file.read()).hexdigest()


def retrieve_update():
    """Retrieves a new version of the exe."""

    data = get_checksum().encode()

    with urlopen(UPDATE_URL, data=data) as response:
        if response.code == 204:
            raise NoUpdateAvailable()

        return response.read()

def update():
    """Updates the Windows executable."""

    if name != 'nt':
        LOGGER.debug('Not running on Windows. Skipping update process.')
        return

    LOGGER.info('Checking for update.')
    old_path = get_old_path()
    old_path.unlink(exist_ok=True)

    try:
        new_exe = retrieve_update()
    except HTTPError as error:
        LOGGER.error('Could not query update server.')
        LOGGER.debug('Status: %i, reason: %s.', error.status, error.reason)
        return
    except URLError as error:
        LOGGER.error('Could not query update server.')
        LOGGER.debug('Reason: %s.', error.reason)
        return
    except NoUpdateAvailable:
        LOGGER.info('No update available.')
        return

    LOGGER.debug('Renaming current exe to old exe.')
    rename(executable, old_path)

    LOGGER.debug('Writing new exe file.')
    with open(executable, 'wb') as file:
        file.write(new_exe)
        file.flush()

    args = ([executable] + argv)
    LOGGER.debug('Substituting running process with new executable.')
    execl(executable, *args)
