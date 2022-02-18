"""Custom thread locking."""

from threading import Lock as _Lock


__all__ = ['Locked', 'Lock']


class Locked(Exception):
    """Indicates that the lock is currently acquired."""


class Lock(_Lock):
    """A custom thread lock context manager."""

    def __enter__(self):
        if not self.acquire(blocking=False):
            raise Locked()

        return self

    def __exit__(self, *_):
        self.release()
