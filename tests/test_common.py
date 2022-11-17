"""Tests the common.py module."""

from pathlib import Path
from tempfile import TemporaryFile
from unittest import TestCase

from digsigclt.common import copy_file, sha256sum


PATH = Path(__file__).parent.joinpath('testfile.txt')
SHA256 = '1ab1a2bb8502820a83881a5b66910b819121bafe336d76374637aa4ea7ba2616'
CHUNK_SIZE = 1024
SIZE = CHUNK_SIZE ** 2


class TestCopyFile(TestCase):
    """Tests the copy_file() function."""

    def test_copy_file(self):
        """Tests the copy_file() function."""
        with open('/dev/zero', 'rb') as src, TemporaryFile('w+b') as dst:
            copy_file(src, dst, SIZE, chunk_size=CHUNK_SIZE)
            dst.flush()
            dst.seek(0)
            size = len(dst.read())

        self.assertEqual(size, SIZE)


class TestSHA256SUM(TestCase):
    """Tests the sha256sum() function."""

    def test_sha256sum(self):
        """Tests the sha256sum() function."""
        self.assertEqual(sha256sum(PATH), SHA256)
        self.assertEqual(sha256sum(str(PATH)), SHA256)
