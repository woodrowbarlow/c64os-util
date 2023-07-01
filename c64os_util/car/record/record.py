"""
Classes and methods relating to archive records.
"""

import abc
import copy
import io
import typing

from ...util import copy_buffer
from ..common import CarCompressionType, CarRecordType
from .header import ArchiveRecordHeader


class ArchiveRecord(abc.ABC):
    """
    ``ArchiveRecord`` is the base class for all records (files and directories) within
    the archive. ``ArchiveRecord`` is abstract and cannot be instantiated; instead, an
    instance of one of the derived classes (``ArchiveFile`` or ``ArchiveDirectory``)
    should be created.
    """

    @property
    def header(self) -> ArchiveRecordHeader:
        """
        Get this record's header.

        :return: The record header.
        """
        return ArchiveRecordHeader(
            name=self.name,
            size=self.size,
            record_type=self.record_type,
            compression_type=self.compression_type,
        )

    @property
    def name(self) -> str:
        """
        Get the record name.

        :return: The record name.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Set the record name.

        :param value: The new record name.
        """
        assert len(value) <= ArchiveRecordHeader.MAX_NAME_SIZE
        self._name = value

    @property
    def size(self) -> int:
        """
        Get the record size.

        :return: The record size.
        """
        # must be implemented in derived class
        raise NotImplementedError()

    @property
    def record_type(self) -> CarRecordType:
        """
        Get the record type (file or directory).

        :return: The record type.
        """
        # must be implemented in derived class
        raise NotImplementedError()

    @property
    def compression_type(self) -> CarCompressionType:
        """
        Get the record compression type.

        :return: The record compression type.
        """
        # must be implemented in derived class
        raise NotImplementedError()

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this record into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        # must be implemented in derived class
        raise NotImplementedError()

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "ArchiveRecord":
        """
        Read binary data from a buffer and parse it into a record object.

        :param buffer: The buffer from which to read.
        :return: The parsed record object.
        """
        header = ArchiveRecordHeader.deserialize(buffer)
        if header.record_type.is_directory():
            # pylint: disable=W0212
            return ArchiveDirectory._deserialize(header, buffer)
        return ArchiveFile._deserialize(header, buffer)  # pylint: disable=W0212


class ArchiveFile(ArchiveRecord, io.BytesIO):  # type: ignore
    """
    An ``ArchiveFile`` represents a single file within the archive.
    """

    def __init__(
        self,
        name: str = "",
        file_type: CarRecordType = CarRecordType.SEQFILE,
        compression_type: CarCompressionType = CarCompressionType.NONE,
    ):
        """
        Create a new file record.

        :param name: The name of this file (not full path).
        :param buffer: The underlying buffer for this file.
        :param file_type: The record type (SEQ or PRG).
        :param compression_type: The compression type. (Only NONE is supported.)
        """
        self.name = name
        self.file_type = file_type
        self.compression_type = compression_type
        super().__init__()

    @property
    def size(self) -> int:
        """
        Get the record size. (Size of file in bytes.)

        :return: The record size.
        """
        return self.getbuffer().nbytes

    @property
    def record_type(self):
        """
        Get the file type (SEQ or PRG).

        :return: The file type.
        """
        return self.file_type

    @property
    def file_type(self) -> CarRecordType:
        """
        Get the file type (SEQ or PRG).

        :return: The file type.
        """
        return self._file_type

    @file_type.setter
    def file_type(self, value: CarRecordType):
        """
        Set the file type (SEQ or PRG).

        :param value: The new file type.
        """
        self._file_type = value

    @property
    def compression_type(self) -> CarCompressionType:
        """
        Get the file compression type. (Only NONE is supported.)

        :return: The file compression type.
        """
        return self._compression_type

    @compression_type.setter
    def compression_type(self, value: CarCompressionType):
        """
        Set the file compression type. (Only NONE is supported.)

        :param value: The new file compression type.
        """
        self._compression_type = value

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this record into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        self.header.serialize(buffer)
        self.seek(0)
        copy_buffer(self, buffer)

    @staticmethod
    def _deserialize(
        header: ArchiveRecordHeader, buffer: typing.BinaryIO
    ) -> "ArchiveFile":
        """
        Read binary data from a buffer and parse it into a record object.

        :param header: The header (parsed from the buffer already).
        :param buffer: The buffer from which to read.
        :return: The parsed file record object.
        """
        record = ArchiveFile(
            name=header.name,
            file_type=header.record_type,
            compression_type=header.compression_type,
        )
        copy_buffer(buffer, record, max_size=header.size)
        return record


class ArchiveDirectory(ArchiveRecord, list):
    """
    ArchiveDirectory is used to represent directories within a C64 archive. As
    in a filesystem, archive directories can contain files or other (nested)
    directories. In an archive, a directory cannot have more than one entry
    with the same name (names must be unique among children) -- even if one of
    those entries is a directory and the other is a file.

    ArchiveDirectory is a list; children can be directly inserted or removed.instance
    Inserting a new child can raise a ValueError if the directory already has
    a child of the same name.

    ArchiveDirectory also support dict-style indexing to look up children by
    name. This syntax only supports read operations.

    Example: ::

        d = ArchiveDirectory(name='test')
        d.append(ArchiveDirectory(name='nested'))
        d += [ ArchiveFile(name='foo'), ArchiveFile(name='bar') ]
        for record in d:
            print(record.name)
        print(d['foo'].file_type)
        print(d['bar'].file_type)
    """

    def __init__(
        self, name: str = "", iterable: typing.Optional[list[ArchiveRecord]] = None
    ):
        """
        Create a new directory record.

        :param name: The name of this file (not full path).
        :param iterable: Collection of records which should be added to the directory.
        """
        self.name = name
        if iterable is None:
            iterable = []
        super().__init__(self._validate(item) for item in iterable)

    @property
    def size(self) -> int:
        """
        Get the record size. (Number of children.)

        :return: The record size.
        """
        return len(self)

    @property
    def record_type(self) -> CarRecordType:
        """
        Get the record type for directories.

        :return: The record type (DIRECTORY).
        """
        return CarRecordType.DIRECTORY

    @property
    def compression_type(self) -> CarCompressionType:
        """
        Get the record compression type. (Always NONE for directories.)

        :return: The record compression type.
        """
        return CarCompressionType.NONE

    def get_child(self, name: str) -> typing.Optional[ArchiveRecord]:
        """
        Get a child record by name.

        :return: The child record, or None if no children exist by that name.
        """
        for child in self:
            if child.name == name:
                return child
        return None

    def keys(self):
        """
        Get a list of the names of all records in this directory.

        :return: List of record names.
        """
        return [child.name for child in self]

    def values(self):
        """
        Get a list of all records in this directory.

        :return: List of records.
        """
        return self

    def items(self) -> typing.List[typing.Tuple[str, ArchiveRecord]]:
        """
        Get a list of key-value pairs for all records in this directory. The key is the
        record name, and the value is the record itself.

        :return: List of key-value pairs.
        """
        return list(zip(self.keys(), self.values()))

    def __getitem__(self, arg):
        """
        Get a child record by numeric index, or by name.

        :return: The matching record.
        """
        if isinstance(arg, int):
            return super().__getitem__(arg)
        child = self.get_child(arg)
        if child is not None:
            return child
        raise KeyError(f"{self.name} does not contain {arg}")

    def __setitem__(self, index, item):
        """
        Set the child record at the specified numeric index.

        :param index: The list index to override.
        :param item: The new list item.
        """
        super().__setitem__(index, self._validate(item))

    def __add__(self, other):
        """
        Concatenate this directory's children with the provided list.
        If the provided list is another directory, it will be merged with this.

        :param other: List to be concatenated.
        :return: A directory with the list concatenated.
        """
        if isinstance(other, ArchiveDirectory):
            dup = copy.deepcopy(self)
            dup.merge(other)
            return dup
        return super().__add__(other)

    def __contains__(self, other):
        """
        Check whether the given record is contained within this directory.
        If a string is provided instead of a record, this will check if a record by
        that name exists within this directory.
        """
        if isinstance(other, str):
            return self.get_child(other) is not None
        return super().__contains__(other)

    def insert(self, index, item):
        """
        Insert the given record as a child of this directory at the given index.
        """
        super().insert(index, self._validate(item))

    def append(self, item):
        """
        Append the given record as a child of this directory.
        """
        super().append(self._validate(item))

    def extend(self, other):
        """
        Append all the items in the given list as children of this directory.
        """
        super().extend(self._validate(item) for item in other)

    def _validate(self, record: ArchiveRecord) -> ArchiveRecord:
        """
        Pre-process a record before inserting it.
        This checks to be sure there are no name collisions, and updates the parent.

        :param record: The record to be inserted.
        """
        if not isinstance(record, ArchiveRecord):
            raise ValueError("a directory can only contain files or other directories")
        child = self.get_child(record.name)
        if child is not None:
            raise ValueError(
                "a directory or file already exists in "
                f"{self.name} with name {child.name}"
            )
        return record

    def merge(self, other: "ArchiveDirectory"):
        """
        Merge the contents of another directory into this directory.

        :param other: The other directory.
        """
        if other.name != self.name:
            raise ValueError("directories must have the same name to be merged")
        for child in other:
            try:
                self_child = self[child.name]
            except KeyError:
                self.append(child)
                continue
            if not isinstance(child, ArchiveDirectory):
                raise ValueError(
                    f"both directories contain a record named {child.name}"
                )
            if not isinstance(self_child, ArchiveDirectory):
                raise ValueError(
                    f"both directories contain a record named {child.name}"
                )
            self_child.merge(child)

    def directories(self):
        """
        A generator which iterates through all directories that are direct children of
        this one.
        """
        for child in self:
            if not isinstance(child, ArchiveDirectory):
                continue
            yield child

    def files(self):
        """
        A generator which iterates through all files that are direct children of this
        directory.
        """
        for child in self:
            if not isinstance(child, ArchiveFile):
                continue
            yield child

    def _walk(self, path):
        """
        A generator which visits each directory in the archive (in order, recursively).

        :param path: The starting path (forms the prefix of what will be returned).
        :return: The directory's path (represented as a list) and the directory record
            itself.
        """
        path.append(self.name)
        yield path, self
        for record in self.directories():
            yield from record._walk(path)  # pylint: disable=W0212

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this record into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        self.header.serialize(buffer)
        for child in self:
            child.serialize(buffer)

    @staticmethod
    def _deserialize(
        header: ArchiveRecordHeader, buffer: typing.BinaryIO
    ) -> "ArchiveDirectory":
        """
        Read binary data from a buffer and parse it into a record object.

        :param header: The header (parsed from the buffer already).
        :param buffer: The buffer from which to read.
        :return: The parsed directory record object.
        """
        directory = ArchiveDirectory(name=header.name)
        for _ in range(header.size):
            child = ArchiveRecord.deserialize(buffer)
            directory.append(child)
        return directory
