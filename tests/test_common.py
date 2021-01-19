"""Tests the common.py module."""

from json import dumps
from pathlib import Path
from unittest import TestCase

from digsigclt.common import FileInfo


CONTENT = 'Hello, world.\n'
PATH = Path(__file__).parent.joinpath('testfile.txt')
CTIME = 1611050058.40735
SHA256 = '1ab1a2bb8502820a83881a5b66910b819121bafe336d76374637aa4ea7ba2616'
JSON = {'sha256sum': SHA256, 'ctime': CTIME}


class TestFileInfo(TestCase):
    """Test the FileInfo class."""

    def _test_file_info(self, file_info: FileInfo):
        """Tests a FileInfo object."""
        self.assertEqual(file_info.sha256sum, SHA256)
        self.assertEqual(file_info.ctime, CTIME)
        self.assertEqual(file_info.to_json(), JSON)
        self.assertEqual(str(file_info), dumps(JSON))
        self.assertEqual(bytes(file_info), dumps(JSON).encode())

    def _test_from_file_str(self):
        """Tests with a file created from a str."""
        self._test_file_info(FileInfo.from_file(str(PATH)))

    def _test_from_file_path(self):
        """Tests with a file created from a Path."""
        self._test_file_info(FileInfo.from_file(PATH))

    def test_from_file(self):
        """Tests the FileInfo.from_file classmethod."""
        self._test_from_file_str()
        self._test_from_file_path()
