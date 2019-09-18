"""System adminstration command handling."""

from os import name
from subprocess import CalledProcessError, check_call


__all__ = ['http_beep']


def beep():
    """Performs a speaker beep to identify the system."""

    if name == 'posix':
        return check_call('/usr/bin/beep')

    if name == 'nt':
        return check_call('@echo \x07', shell=True)

    raise NotImplementedError()


def http_beep():
    """Runs the beep function, handles exceptions
    and returns a JSON response and a HTTP status code.
    """

    try:
        beep()
    except CalledProcessError as cpe:
        json = {'message': 'Could not beep.', 'error': str(cpe)}
        status_code = 500
    except NotImplementedError:
        json = {
            'message': 'Could not beep.',
            'error': 'Beeping is not implemented on this platform.'
        }
        status_code = 501
    else:
        json = {'message': 'System should have beeped.'}
        status_code = 200

    return (json, status_code)
