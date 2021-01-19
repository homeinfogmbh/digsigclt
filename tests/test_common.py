"""Tests the common.py module."""

from json import dumps
from pathlib import Path
from tempfile import TemporaryFile
from unittest import TestCase

from digsigclt.common import FileInfo, copy_file, sha256sum


CONTENT = 'Hello, world.\n'
PATH = Path(__file__).parent.joinpath('testfile.txt')
CTIME = 1611050058.40735
SHA256 = '1ab1a2bb8502820a83881a5b66910b819121bafe336d76374637aa4ea7ba2616'
JSON = {'sha256sum': SHA256, 'ctime': CTIME}
CHUNK_SIZE = 1024
SIZE = CHUNK_SIZE ** 2


class TestFileInfo(TestCase):
    """Test the FileInfo class."""

    def _test_file_info(self, file_info: FileInfo):
        """Tests a FileInfo object."""
        self.assertEqual(file_info.sha256sum, SHA256)
        self.assertEqual(file_info.ctime, CTIME)
        self.assertEqual(file_info.to_json(), JSON)
        self.assertEqual(str(file_info), dumps(JSON))
        self.assertEqual(bytes(file_info), dumps(JSON).encode())

    def test_from_file(self):
        """Tests the FileInfo.from_file classmethod."""
        self._test_file_info(FileInfo.from_file(PATH))
        self._test_file_info(FileInfo.from_file(str(PATH)))


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
