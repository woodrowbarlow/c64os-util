import datetime
import os
import io
import unittest

from c64os_util.car import (
    C64Archive, ArchiveFile, ArchiveDirectory,
    CarArchiveType, CarRecordType, CarCompressionType,
)


class TestArchive(unittest.TestCase):

    def test_file(self):
        f = ArchiveFile(name='foo')
        f.write('hello world'.encode('petscii_c64en_lc'))
        assert f.size == len('hello world')
        f.seek(0)
        data = f.read().decode('petscii_c64en_lc')
        assert data == 'hello world'


    def test_directory(self):
        root = ArchiveDirectory(name='root')
        root += [
            ArchiveDirectory(name='foo'),
            ArchiveFile(name='bar'),
        ]
        assert len(root) == 2
        assert root['foo'] == root[0]
        assert root['bar'] == root[1]
        assert root['bar'] != root['foo']
        with self.assertRaises(ValueError):
            root.append(ArchiveDirectory('bar'))


    def test_deserialize(self):
        path = os.path.join('tests', 'data', 'test.car')
        with open(path, 'rb') as f:
            archive = C64Archive.deserialize(f)
        self._assert_archive(archive)


    def test_serialize(self):
        timestamp = datetime.datetime(
            year=2022, month=5, day=13,
            hour=3, minute=27,
        )
        archive = C64Archive(
            archive_type=CarArchiveType.GENERAL,
            timestamp=timestamp, note='hello world'
        )
        archive.root = ArchiveDirectory(name='test')
        archive.root.append(
            ArchiveFile(
                name='untitled.t',
                file_type=CarRecordType.SEQFILE,
                compression_type=CarCompressionType.NONE
            )
        )
        with io.BytesIO() as f:
            archive.serialize(f)
            f.seek(0)
            archive = C64Archive.deserialize(f)
        assert archive.header.note == 'hello world'
        self._assert_archive(archive)
    

    def _assert_archive(self, archive):
        assert archive.header.timestamp.year == 2022
        assert archive.header.timestamp.month == 5
        assert archive.header.timestamp.day == 13
        assert archive.header.timestamp.hour == 3
        assert archive.header.timestamp.minute == 27
        assert archive.header.archive_type == CarArchiveType.GENERAL
        assert isinstance(archive.root, ArchiveDirectory)
        assert archive.root.name == 'test'
        assert isinstance(archive.root['untitled.t'], ArchiveFile)
        assert archive.root['untitled.t'].file_type == CarRecordType.SEQFILE
        assert archive.root['untitled.t'].compression_type == CarCompressionType.NONE
