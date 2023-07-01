import datetime
import typing
import os

from .common import CarArchiveType, CarRecordType, CarCompressionType
from .header import ArchiveHeader
from .record import ArchiveRecord, ArchiveDirectory, ArchiveFile
from ..util import LC_CODEC, copy_buffer


class C64Archive:

    def __init__(
        self, archive_type: CarArchiveType = CarArchiveType.GENERAL,
        timestamp: datetime.datetime = datetime.datetime.utcnow(), note: str = ''
    ):
        self.header = ArchiveHeader(archive_type=archive_type, timestamp=timestamp, note=note)
        self.root = None


    @property
    def header(self) -> ArchiveHeader:
        return self._header


    @header.setter
    def header(self, value: ArchiveHeader):
        self._header = value


    @property
    def root(self) -> ArchiveRecord:
        return self._root


    @root.setter
    def root(self, value: ArchiveRecord):
        self._root = value


    def _find_path(
        self, start: ArchiveRecord, path: typing.List[str],
        create_directories: bool = False,
    ):
        head = path[0]
        path = path[1:]
        if start is None or start.name != head:
            raise ValueError()
        if not len(path):
            return start
        if isinstance(start, ArchiveFile):
            raise ValueError()
        head = path[0]
        if create_directories and head not in start:
            start += [ ArchiveDirectory(name=head) ]
        start = start[head]
        return self._find_path(start, path, create_directories=create_directories)


    def __insert_path(
        self, child: ArchiveRecord, path: typing.List[str],
        create_missing: bool = False,
    ):
        if len(path):
            if create_missing and self.root is None:
                self.root = ArchiveDirectory(name=path[-1])
            parent = self._find_path(self.root, path, create_directories=create_missing)
            parent += [ child ]
            return
        if self.root is not None:
            raise ValueError()
        self.root = child
            

    def ls(self, path: str, sep: str = os.path.sep):
        parts = path.split(sep)
        return self._find_path(self.root, parts)


    def rm(self, path: str, sep: str = os.path.sep, missing_ok: bool = False, recursive: bool = False):
        parts = path.split(sep)
        tail = parts[-1]
        parts = parts[:-1]
        if not len(parts):
            if self.root is not None and self.root.name == tail:
                if isinstance(self.root, ArchiveDirectory):
                    if self.root.size and not recursive:
                        raise ValueError()
                self.root = None
                return
            if not missing_ok:
                raise ValueError()
            return
        parent = self._find_path(self.root, parts)
        if parent is None:
            if not missing_ok:
                raise ValueError()
            return
        if not missing_ok:
            if tail not in parent:
                raise ValueError()
        if isinstance(parent[tail], ArchiveDirectory):
            if parent[tail].size and not recursive:
                raise ValueError()
        for i, child in enumerate(parent):
            if child.name == tail:
                del parent[i]
                return
        raise ValueError()


    def mkdir(
        self, path: str, sep: str = os.path.sep,
        create_missing: bool = False, exists_ok: bool = False,
    ):
        try:
            record = self.ls(path, sep=sep)
        except (ValueError, KeyError):
            parts = path.split(sep)
            tail = parts[-1]
            parts = parts[:-1]
            record = ArchiveDirectory(name=tail)
            self.__insert_path(record, parts, create_missing=create_missing)
            return record
        if not isinstance(record, ArchiveDirectory):
            raise ValueError()
        if not exists_ok:
            raise ValueError()
        return record


    def touch(
        self, path: str, sep: str = os.path.sep,
        file_type: CarRecordType = CarRecordType.SEQFILE,
        compression_type: CarCompressionType = CarCompressionType.NONE,
        create_directories: bool = False, buffer: typing.BinaryIO = None,
    ):
        try:
            record = self.ls(path, sep=sep)
        except (ValueError, KeyError):
            parts = path.split(sep)
            tail = parts[-1]
            parts = parts[:-1]
            record = ArchiveFile(name=tail, file_type=file_type, compression_type=compression_type)
            self.__insert_path(record, parts, create_missing=create_directories)
            if buffer is not None:
                copy_buffer(buffer, record)
            return record
        raise ValueError()


    def walk(self):
        if self.root is None or not isinstance(self.root, ArchiveDirectory):
            return
        yield from self.root._walk(path=[])


    def __iter__(self):
        if self.root is None:
            return
        if not isinstance(self.root, ArchiveDirectory):
            yield self.root
            return
        for path, record in self.walk():
            for r in record.files():
                yield path + [ r.name ], r


    def __getitem__(self, arg):
        if self.root is None:
            raise KeyError()
        if isinstance(arg, int):
            if arg == 0:
                return self.root
            raise KeyError()
        if self.root.name == arg:
            return self.root
        raise KeyError()


    def __contains__(self, other):
        if self.root is None:
            return False
        if isinstance(other, str):
            return self.root.name == other
        return self.root == other


    def serialize(self, buffer: typing.BinaryIO):
        self.header.serialize(buffer)
        if self.root is not None:
            self.root.serialize(buffer)


    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> 'C64Archive':
        header = ArchiveHeader.deserialize(buffer)
        archive = C64Archive(
            archive_type=header.archive_type,
            timestamp=header.timestamp.to_datetime(),
            note=header.note,
        )
        archive.root = ArchiveRecord.deserialize(buffer)
        return archive
