import abc
import typing

from .header import ArchiveRecordHeader
from ..common import CarRecordType, CarCompressionType


class ArchiveRecord(abc.ABC):

    @property
    def header(self) -> ArchiveRecordHeader:
        """
        Get this record's header.

        :return: The record header.
        """
        return ArchiveRecordHeader(
            name = self.name,
            size = self.size,
            record_type = self.record_type,
            compression_type = self.compression_type,
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
    def deseralize(buffer: typing.BinaryIO) -> 'ArchiveRecord':
        """
        Read binary data from a buffer and parse it into a record object.
        
        :param buffer: The buffer from which to read.
        :return: The parsed record object.
        """
        header = ArchiveRecordHeader.deseralize(buffer)
        if header.record_type.is_directory():
            return ArchiveDirectory._deseralize(header, buffer)
        return ArchiveFile._deseralize(header, buffer)
