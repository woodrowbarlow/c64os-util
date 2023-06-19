import unittest

from c64os_util import (
    CarArchiveType, CarRecordType, CarCompressionType,
    CbmArchive, ArchiveDirectoryRecord, ArchiveFileRecord,
)


class TestCbmArchive(unittest.TestCase):

    def test_foo(self):
        archive = CbmArchive(note='hello world')
        archive.touch(
            'example-app/main.o',
            file_type=CarRecordType.PRGFILE,
            create_directories=True,
        )
        for record in archive:
            print(record.path())
