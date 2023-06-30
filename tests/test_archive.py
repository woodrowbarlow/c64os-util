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


    def test_merge(self):
        a = ArchiveDirectory(name='root')
        b = ArchiveDirectory(name='root')
        c = ArchiveDirectory(name='inner')
        d = ArchiveFile(name='foo.t')
        e = ArchiveFile(name='bar.t')
        f = ArchiveFile(name='baz.t')
        a += [ d, f ]
        c += [ d, e ]
        b += [ c ]
        with self.assertRaises(ValueError):
            b + c
        merged = a + b
        assert merged.name == 'root'
        assert len(merged) == 3
        assert 'inner' in merged
        assert 'foo.t' in merged
        assert 'baz.t' in merged
        assert len(merged['inner']) == 2
        assert 'foo.t' in merged['inner']
        assert 'bar.t' in merged['inner']
        b += [ d ]
        with self.assertRaises(ValueError):
            a + b


    def test_ls(self):
        archive = self._create_archive()
        archive.root = ArchiveDirectory(name='root')
        archive['root'].append(ArchiveDirectory(name='inner'))
        archive['root']['inner'].append(ArchiveFile(name='foo.t'))
        record = archive.ls('root', sep='/')
        assert isinstance(record, ArchiveDirectory)
        assert record == archive['root']
        record = archive.ls('root/inner', sep='/')
        assert isinstance(record, ArchiveDirectory)
        assert record == archive['root']['inner']
        record = archive.ls('root/inner/foo.t', sep='/')
        assert isinstance(record, ArchiveFile)
        assert record == archive['root']['inner']['foo.t']


    def test_mkdir(self):
        archive = self._create_archive()
        record = archive.mkdir('root', sep='/')
        assert 'root' in archive
        assert isinstance(archive['root'], ArchiveDirectory)
        assert archive['root'].size == 0
        assert record == archive['root']
        with self.assertRaises(ValueError):
            archive.mkdir('other', sep='/')
        record = archive.mkdir('root/inner', sep='/')
        assert archive['root'].size == 1
        assert 'inner' in archive['root']
        assert isinstance(archive['root']['inner'], ArchiveDirectory)
        assert record == archive['root']['inner']
        with self.assertRaises(ValueError):
            archive.mkdir('root/inner', sep='/')
        archive.mkdir('root/inner', sep='/', exists_ok=True)
        assert archive['root'].size == 1
        with self.assertRaises(ValueError):
            archive.mkdir('root/deeper/nested', sep='/')
        record = archive.mkdir('root/deeper/nested', sep='/', create_missing=True)
        assert 'deeper' in archive['root']
        assert 'nested' in archive['root']['deeper']
        assert isinstance(archive['root']['deeper']['nested'], ArchiveDirectory)
        assert record == archive['root']['deeper']['nested']
        archive['root'].append(ArchiveFile(name='dummy'))
        with self.assertRaises(ValueError):
            archive.mkdir('root/dummy', sep='/')
        with self.assertRaises(ValueError):
            archive.mkdir('root/dummy', sep='/', exists_ok=True)


    def test_deserialize(self):
        path = os.path.join('tests', 'data', 'test.car')
        with open(path, 'rb') as f:
            archive = C64Archive.deserialize(f)
        self._assert_archive(archive)


    def test_serialize(self):
        archive = self._create_archive()
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


    def _create_archive(self):
        timestamp = datetime.datetime(
            year=2022, month=5, day=13,
            hour=3, minute=27,
        )
        archive = C64Archive(
            archive_type=CarArchiveType.GENERAL,
            timestamp=timestamp, note='hello world'
        )
        return archive
    

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
