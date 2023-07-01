"""
Each record within the archive contains a record header. This module provides utilities
for parsing or generating that header.
"""

import typing

from ...util import LC_CODEC
from ..common import CarCompressionType, CarRecordType


class ArchiveRecordHeader:
    """
    An ``ArchiveRecordHeader`` represents a de-serialized record header. It provides
    properties to access the underlying fields.
    """

    MAX_NAME_SIZE = 15

    def __init__(
        self,
        name: str = "",
        size: int = 0,
        record_type: CarRecordType = CarRecordType.SEQFILE,
        compression_type: CarCompressionType = CarCompressionType.NONE,
    ):
        """
        Create a new record header.

        :param name: The name of this record (not full path).
        :param size: The size of this record.
        :param record_type: The record type (file or directory).
        :param compression_type: The compression type. (Only NONE is supported.)
        """
        self._record_type = record_type
        self._size = size
        self._name = name
        self._compression_type = compression_type

    @property
    def record_type(self) -> CarRecordType:
        """
        Get the record type (file or directory).

        :return: The record type.
        """
        return self._record_type

    @property
    def size(self) -> int:
        """
        Get the record size.

        :return: The record size.
        """
        return self._size

    @property
    def name(self) -> str:
        """
        Get the record name.

        :return: The record name.
        """
        return self._name

    @property
    def compression_type(self) -> CarCompressionType:
        """
        Get the record compression type. (Only NONE is supported.)

        :return: The record compression type.
        """
        return self._compression_type

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this header into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        self.record_type.serialize(buffer)
        buffer.write(b"\0")  # lock byte?
        buffer.write(self.size.to_bytes(3, "little"))
        name_bytes = self.name.encode(LC_CODEC)
        name_bytes = name_bytes.ljust(ArchiveRecordHeader.MAX_NAME_SIZE, b"\xA0")
        buffer.write(name_bytes)
        buffer.write(b"\0")  # ???
        self.compression_type.serialize(buffer)

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "ArchiveRecordHeader":
        """
        Read binary data from a buffer and parse it into a record header.

        :param buffer: The buffer from which to read.
        :return: The parsed record header object.
        """
        record_type = CarRecordType.deserialize(buffer)
        buffer.read(1)  # lock byte?
        size = int.from_bytes(buffer.read(3), "little")
        name_bytes = buffer.read(ArchiveRecordHeader.MAX_NAME_SIZE)
        name = name_bytes.rstrip(b"\xA0").decode(LC_CODEC)
        buffer.read(1)  # ???
        compression_type = CarCompressionType.deserialize(buffer)
        return ArchiveRecordHeader(
            name=name,
            size=size,
            record_type=record_type,
            compression_type=compression_type,
        )
