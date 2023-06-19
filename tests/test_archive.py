import unittest

from c64os_util import (
    CarArchiveType, CarRecordType, CarCompressionType,
    CbmArchive, ArchiveDirectoryRecord, ArchiveFileRecord,
)


class TestCbmArchive(unittest.TestCase):

    def test_foo(self):
        archive = CbmArchive(note='hello world')
        with archive('example-app/data/info.t', 'w') as f:
            print('hello', file=f)
            print('world', file=f)
        with archive('example-app/data/info.t', 'r') as f:
            for line in f:
                print(line)
