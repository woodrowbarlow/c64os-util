import io
import typing

from .record import ArchiveRecord
from .header import ArchiveRecordHeader
from ..common import CarRecordType, CarCompressionType


class ArchiveFile(ArchiveRecord, io.BytesIO):


    def __init__(
        self, name: str = '',
        file_type: CarRecordType = CarRecordType.SEQFILE,
        compression_type: CarCompressionType = CarCompressionType.NONE,
        *args, **kwargs,
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
        super().__init__(*args, **kwargs)


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
        copy_buffer(self, buffer, src_whence=os.SEEK_SET)


    @staticmethod
    def _deseralize(header: ArchiveRecordHeader, buffer: typing.BinaryIO) -> 'ArchiveFile':
        """
        Read binary data from a buffer and parse it into a record object.
        
        :param header: The header (parsed from the buffer already).
        :param buffer: The buffer from which to read.
        :return: The parsed file record object.
        """
        record = ArchiveFile(
            name=header.name,
            file_type=header.record_type,
            compression_type=header.compression_type
        )
        copy_buffer(buffer, record, max_size=header.size)
        return record
