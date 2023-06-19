import datetime
import os

from c64os_util.schema.util import BaseSchema
from c64os_util.schema.car.record import ArchiveDirectoryRecord
from c64os_util.schema.car.header import ArchiveHeader
from c64os_util.schema.car.common import CarArchiveType, CarRecordType, CarCompressionType


class ArchiveIterator:

    def __init__(self, start):
        self.records = []
        if isinstance(start, ArchiveDirectoryRecord):
            for record in start.walk():
                self.records += list(record.files())
        else:
            self.records.append(start)
        self.idx = 0


    def __next__(self):
        if self.idx >= len(self.records):
            raise StopIteration
        idx = self.idx
        self.idx += 1
        return self.records[idx]


class CbmArchive(BaseSchema):

    def __init__(
        self, archive_type=CarArchiveType.GENERAL,
        timestamp=datetime.datetime.utcnow(), note='',
        root=None
    ):
        self._header = ArchiveHeader(
            archive_type, timestamp, note
        )
        self._root = root


    @property
    def header(self):
        return self._header


    @property
    def root(self):
        return self._root


    def ls(self, path, sep=os.path.sep):
        if not self.root:
            raise FileNotFoundError()
        parts = path.split(sep)
        if not parts:
            raise FileNotFoundError()
        return self._ls(self.root, parts[0], parts[1:])


    def _ls(record, name, parts):
        if record.name != name:
            raise FileNotFoundError()
        if not parts:
            return record
        if not isinstance(record, ArchiveDirectoryRecord):
            raise FileNotFoundError()
        name = parts[0]
        parts = parts[1:]
        for child in record:
            if child.name == name:
                return self._ls(child, name, parts)
        raise FileNotFoundError()


    def rm(self, path, sep=os.path.sep, recursive=False):
        record = self.ls(path, sep=sep)
        if not recursive:
            if isinstance(record, ArchiveDirectoryRecord) and len(record):
                raise ValueError("directory is not empty")
        record.parent.remove(record)


    def mkdir(self, path, sep=os.path.sep, create_missing=False):
        parts = path.split(sep)
        if not parts:
            raise ValueError('invalid path')
        self._root = self._mkdir(self.root, parts[0], parts[1:], create_missing)


    def _mkdir(self, record, name, parts, create_missing):
        if record is None:
            if parts and not create_missing:
                raise FileNotFoundError()
            record = ArchiveDirectoryRecord(name)
        if record.name != name:
            raise ValueError('cannot have more than one root')
        if not parts:
            return record
        name = parts[0]
        parts = parts[1:]
        child = record.get_child(name)
        child = self._mkdir(child, name, parts, create_missing)
        record.add(child)
        return record


    def touch(
        self, path, file_type=CarRecordType.SEQFILE,
        compression_type=CarCompressionType.NONE,
        sep=os.path.sep, create_directories=False
    ):
        parts = path.split(sep)
        if not parts:
            raise ValueError('invalid path')
        parent_path = sep.join(parts[:-1])
        name = parts[0]
        if create_directories:
            self.mkdir(parent_path, sep=sep, create_missing=True)
        if parent_path:
            parent = self.ls(parent_path, sep=sep)
        child = ArchiveFileRecord(name, file_type, compression_type)
        if parent:
            parent.add(child)
        else:
            self._root = child


    def __iter__(self):
        return ArchiveIterator(self.root)


    def __call__(self, path, sep=os.path.sep):
        # TODO this is going to be the mega function.
        # it's going to behave like python's open call.
        # this needs to return a context manager.
        # it will be used like:
        #   with open('archive.car', 'rb') as f:
        #     archive = CbmArchive.deserialize(f)
        #   codec = 'petscii_c64en_lc'
        #   with archive('app/data/db.t', 'r', encoding=codec) as f:
        #     for line in f:
        #       print(line)
        #   with archive('app/main.o', 'wb') as f1,
        #        open('local/out/main.o', 'rb') as f2:
        #     f1.write(f2.read())
        return self.get_path(path, sep=sep)


    def serialize(self, buffer):
        self.header.serialize(buffer)
        if self.root:
            self.root.serialize(buffer)


    @staticmethod
    def deserialize(buffer):
        header = ArchiveHeader.deseralize(buffer)
        root = ArchiveRecord.deseralize(buffer)
        return CbmArchive(
            archive_type=header.archive_type,
            timestamp=header.timestamp.datetime,
            note=header.note, root=root
        )
