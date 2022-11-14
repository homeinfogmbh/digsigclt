"""Custom thread locking."""

from threading import Lock as _Lock


__all__ = ['Locked', 'Lock']


class Locked(Exception):
    """Indicate that the lock is currently acquired."""


class Lock:
    """A custom thread lock context manager."""

    def __init__(self):
        self._lock = _Lock()    # _Lock() is a function!

    def __enter__(self):
        if not self._lock.acquire(blocking=False):
            raise Locked()

        return self

    def __exit__(self, *_):
        self._lock.release()
