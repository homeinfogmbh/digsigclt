"""Takes screenshots."""

from subprocess import check_call
from tempfile import NamedTemporaryFile

from digsigclt.os.posix.common import SCROT
from digsigclt.types import Screenshot


__all__ = ['screenshot']


JPEG = 'image/jpeg'
FORMATS = {
    'jpe': JPEG,
    'jpeg': JPEG,
    'jpg': JPEG,
    'png': 'image/png',
    'gif': 'image/gif'
}


def screenshot(
        filetype: str = 'jpg',
        display: str = ':0',
        quality: int = None,
        multidisp: bool = False,
        pointer: bool = False
) -> Screenshot:
    """Takes a screenshot."""

    try:
        content_type = FORMATS[filetype]
    except KeyError:
        raise ValueError('Invalid image file type.') from None

    command = [SCROT, '--silent', '--overwrite', '--display', display]

    if quality is not None:
        command += ['--quality', str(quality)]

    if multidisp:
        command.append('--multidisp')

    if pointer:
        command.append('--pointer')

    with NamedTemporaryFile(suffix=f'.{filetype}') as file:
        command.append(file.name)
        check_call(command)
        return Screenshot(file.read(), content_type)
