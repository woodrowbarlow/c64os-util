import typing

from .record import ArchiveRecord
from .header import ArchiveRecordHeader
from .file import ArchiveFile
from ..common import CarRecordType, CarCompressionType


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

    def __init__(self, name: str = '', iterable: list[ArchiveRecord] = None):
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


    def get_child(self, name: str) -> ArchiveRecord:
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
        return [ child.name for child in self ]


    def values(self):
        """
        Get a list of all records in this directory.

        :return: List of records.
        """
        return self


    def items(self):
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
        raise KeyError(f'{self.name} does not contain {arg}')


    def __setitem__(self, index: int, item: ArchiveRecord):
        """
        Set the child record at the specified numeric index.

        :param index: The list index to override.
        :param item: The new list item.
        """
        super().__setitem__(index, self._validate(item))


    def insert(self, index: int, item: ArchiveRecord):
        super().insert(index, self._validate(item))


    def append(self, item: ArchiveRecord):
        super().append(self._validate(item))


    def extend(self, other: list[ArchiveRecord]):
        super().extend(self._validate(item) for item in other)


    def _validate(self, record: ArchiveRecord) -> ArchiveRecord:
        """
        Pre-process a record before inserting it.
        This checks to be sure there are no name collisions, and updates the parent.

        :param record: The record to be inserted.
        """
        if not isinstance(record, ArchiveRecord):
            raise ValueError(f"a directory can only contain files or other directories")
        child = self.get_child(record.name)
        if child is not None:
            raise ValueError(f"a directory or file already exists in {self.name} with name {child.name}")
        return record


    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this record into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        self.header.serialize(buffer)
        for child in self:
            child.serialize(buffer)


    @staticmethod
    def _deseralize(header: ArchiveRecordHeader, buffer: typing.BinaryIO) -> 'ArchiveDirectory':
        """
        Read binary data from a buffer and parse it into a record object.
        
        :param header: The header (parsed from the buffer already).
        :param buffer: The buffer from which to read.
        :return: The parsed directory record object.
        """
        directory = ArchiveDirectory(name=header.name)
        for _ in range(header.size):
            child = ArchiveRecord.deseralize(buffer)
            directory.append(child)
        return directory
