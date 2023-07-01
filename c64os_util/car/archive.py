"""
High-level API for working with C64 Archives.
"""

import datetime
import os
import typing

from ..util import copy_buffer
from .common import CarArchiveType, CarCompressionType, CarRecordType
from .header import ArchiveHeader
from .record import ArchiveDirectory, ArchiveFile, ArchiveRecord


class C64Archive:
    """
    A ``C64Archive`` represents a deserialized, in-memory, editable archive. It
    provides fields and methods for easily creating and deleting files and folders,
    and for reading and writing the contents of files.
    """

    def __init__(
        self,
        archive_type: CarArchiveType = CarArchiveType.GENERAL,
        timestamp: datetime.datetime = datetime.datetime.utcnow(),
        note: str = "",
    ):
        """
        Create a new ``C64Archive`` object from scratch.

        :param archive_type: The type of archive to create.
        :param timestamp: The archive creation timestamp.
        :param note: A message to store in the archive 'note' field.
        """
        self.header = ArchiveHeader(
            archive_type=archive_type, timestamp=timestamp, note=note
        )
        self.root = None

    @property
    def header(self) -> ArchiveHeader:
        """
        Get the header (metadata) of the archive.

        :return: The header.
        """
        return self._header

    @header.setter
    def header(self, value: ArchiveHeader):
        """
        Set the header (metadata) of the archive.

        :param value: The new header.
        """
        self._header = value

    @property
    def root(self) -> typing.Optional[ArchiveRecord]:
        """
        Get the root record of the archive.

        :return: The root record.
        """
        return self._root

    @root.setter
    def root(self, value: typing.Optional[ArchiveRecord]):
        """
        Set the root record of the archive.

        :param value: The new root record.
        """
        self._root = value

    def _find_path(
        self,
        start: typing.Optional[ArchiveRecord],
        path: typing.List[str],
        create_directories: bool = False,
    ):
        """
        Find the node represented by a given path, relative to the given starting node.

        :param start: The starting node.
        :param path: The relative path from the starting node.
        :param create_directories: If true, missing entries from path will be created
            as directories.
        :return: The request node.
        """
        head = path[0]
        path = path[1:]
        if start is None or start.name != head:
            raise ValueError()
        if not path:
            return start
        if not isinstance(start, ArchiveDirectory):
            raise ValueError()
        head = path[0]
        if create_directories and head not in start:
            start += [ArchiveDirectory(name=head)]
        start = start[head]
        return self._find_path(start, path, create_directories=create_directories)

    def __insert_path(
        self,
        child: ArchiveRecord,
        path: typing.List[str],
        create_missing: bool = False,
    ):
        """
        Insert the given node as a child at the specified (absolute) path.

        :param child: The node to be inserted.
        :param path: The path from the root to the parent.
        :param create_directories: If true, missing entries from path will be created
            as directories.
        """
        if len(path):
            if create_missing and self.root is None:
                self.root = ArchiveDirectory(name=path[-1])
            parent = self._find_path(self.root, path, create_directories=create_missing)
            parent += [child]
            return
        if self.root is not None:
            raise ValueError()
        self.root = child

    def ls(self, path: str, sep: str = os.path.sep):  # pylint: disable=C0103
        """
        Find the record (file or directory) at the given path.

        :param path: A path-like string representing the record's location within the
            archive.
        :param sep: The character used as a path separator (usually '/' or '\\').
        :return: The requested record.
        """
        parts = path.split(sep)
        return self._find_path(self.root, parts)

    def _rm_root(self, name: str, missing_ok: bool, recursive: bool):
        """
        Remove the root node if it matches the given name.

        :param name: The name of the node to remove.
        :param missing_ok: Do not throw an error if the record is missing.
        :param recursive: Delete directories and their contents recursively.
        """
        if self.root is not None and self.root.name == name:
            if isinstance(self.root, ArchiveDirectory):
                if self.root.size and not recursive:
                    raise ValueError()
            self.root = None
            return
        if not missing_ok:
            raise ValueError()

    def rm(  # pylint: disable=C0103
        self,
        path: str,
        sep: str = os.path.sep,
        missing_ok: bool = False,
        recursive: bool = False,
    ):
        """
        Remove the record (file or directory) at the given path.

        :param path: A path-like string representing the record's location within the
            archive.
        :param sep: The character used as a path separator (usually '/' or '\\').
        :param missing_ok: Do not throw an error if the record is missing.
        :param recursive: Delete directories and their contents recursively.
        """
        parts = path.split(sep)
        tail = parts[-1]
        parts = parts[:-1]
        if not parts:
            self._rm_root(tail, missing_ok, recursive)
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
        self,
        path: str,
        sep: str = os.path.sep,
        create_missing: bool = False,
        exists_ok: bool = False,
    ):
        """
        Create a directory at the given path.

        :param path: A path-like string representing the record's location within the
            archive.
        :param sep: The character used as a path separator (usually '/' or '\\').
        :create_missing: Create the parent directories if they do not exist.
        :exists_ok: Do not throw an error if the directory already exists.
        :return: The newly created directory record.
        """
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

    def touch(  # pylint: disable=R0913
        self,
        path: str,
        sep: str = os.path.sep,
        file_type: CarRecordType = CarRecordType.SEQFILE,
        compression_type: CarCompressionType = CarCompressionType.NONE,
        create_directories: bool = False,
        buffer: typing.Optional[typing.BinaryIO] = None,
    ):
        """
        Create a file at the given path.

        :param path: A path-like string representing the record's location within the
            archive.
        :param sep: The character used as a path separator (usually '/' or '\\').
        :file_type: The file type for the new file.
        :compression_type: The compression type for the new file.
        :create_directories: Create the parent directories if they do not exist.
        :buffer: If provided, the contents of this buffer will be written to the file.
        :return: The newly created file record.
        """
        try:
            record = self.ls(path, sep=sep)
        except (ValueError, KeyError):
            parts = path.split(sep)
            tail = parts[-1]
            parts = parts[:-1]
            record = ArchiveFile(
                name=tail, file_type=file_type, compression_type=compression_type
            )
            self.__insert_path(record, parts, create_missing=create_directories)
            if buffer is not None:
                copy_buffer(buffer, record)
                record.seek(0)
            return record
        raise ValueError()

    def walk(self):
        """
        A generator which visits each directory in the archive (in order, recursively).

        :return: The directory's path (represented as a list) and the directory record
            itself.
        """
        if self.root is None or not isinstance(self.root, ArchiveDirectory):
            return
        yield from self.root._walk(path=[])  # pylint: disable=W0212

    def __iter__(self):
        """
        Iterate through each file (not directory) in the archive (in order).

        :return: The file's path (represented as a list) and the file record itself.
        """
        if self.root is None:
            return
        if not isinstance(self.root, ArchiveDirectory):
            yield self.root
            return
        for path, record in self.walk():
            for file_rec in record.files():
                yield path + [file_rec.name], file_rec

    def __getitem__(self, arg):
        """
        Get a child record by name or index.
        Note that there is only one root.

        :param arg: The index or name.
        :return: The root record (if it matches the index or name).
        """
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
        """
        Check if the archive contains a given record.

        :param other: The record in question (or its name).
        :return: True if the archive contains that record, false otherwise.
        """
        if self.root is None:
            return False
        if isinstance(other, str):
            return self.root.name == other
        return self.root == other

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this archive into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        self.header.serialize(buffer)
        if self.root is not None:
            self.root.serialize(buffer)

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "C64Archive":
        """
        Read binary data from a buffer and parse it into an archive object.

        :param buffer: The buffer from which to read.
        :return: The parsed archive object.
        """
        header = ArchiveHeader.deserialize(buffer)
        archive = C64Archive(
            archive_type=header.archive_type,
            timestamp=header.timestamp.to_datetime(),
            note=header.note,
        )
        archive.root = ArchiveRecord.deserialize(buffer)
        return archive
