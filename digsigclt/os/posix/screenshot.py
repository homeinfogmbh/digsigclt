"""Takes screenshots."""

from subprocess import check_call
from tempfile import NamedTemporaryFile

from digsigclt.os.posix.common import SCROT
from digsigclt.types import Screenshot


__all__ = ['screenshot']


FORMATS = {
    '.jpe': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif'
}


def screenshot(suffix: str = '.jpg', display: str = ':0',
               quality: int = None, multidisp: bool = False) -> Screenshot:
    """Takes a screenshot."""

    try:
        content_type = FORMATS[suffix]
    except KeyError:
        raise ValueError('Invalid image file type.') from None

    command = [SCROT, '--display', display]

    if quality is not None:
        command += ['--quality', str(quality)]

    if multidisp:
        command.append('--multidisp')

    with NamedTemporaryFile('w+b', suffix=suffix) as file:
        command.append(file.name)
        check_call(command)
        file.flush()
        file.seek(0)
        return Screenshot(file.read(), content_type)
