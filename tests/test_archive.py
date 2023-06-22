import unittest

from c64os_util.car import (
    ArchiveFile, ArchiveDirectory
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
