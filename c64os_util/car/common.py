"""
Common types and definitions for archive files.
"""

import enum
import typing


class CarArchiveType(enum.Enum):
    """
    The archive header contains a "type" field, which helps C64 OS know what to do with
    the file. This enum defines the possible types.
    """

    GENERAL = 0
    RESTORE = 1
    INSTALL = 2

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this enum into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        buffer.write(self.value.to_bytes(1, "little"))

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "CarArchiveType":
        """
        Read binary data from a buffer and parse it into an object.

        :param buffer: The buffer from which to read.
        :return: The parsed object.
        """
        val = int.from_bytes(buffer.read(1), "little")
        return CarArchiveType(val)


class CarCompressionType(enum.Enum):
    """
    Each file header contains a "compression type" field, which indicates whether the
    file's data has been compressed. This enum defines the supported compression types.
    """

    NONE = 0

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this enum into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        buffer.write(self.value.to_bytes(1, "little"))

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "CarCompressionType":
        """
        Read binary data from a buffer and parse it into an object.

        :param buffer: The buffer from which to read.
        :return: The parsed object.
        """
        val = int.from_bytes(buffer.read(1), "little")
        return CarCompressionType(val)


class CarRecordType(enum.Enum):
    """
    Each record (files and directories) within the archive contain a record_type field.
    This indicates if the record is a file or directory and (if it is a file), which
    type of file (SEQ or PRG).
    """

    PRGFILE = 0x50
    SEQFILE = 0x53
    DIRECTORY = 0x44

    def is_directory(self):
        """
        Check if this enum represents a directory (or something else).
        :return: True if this is a directory.
        """
        return self == CarRecordType.DIRECTORY

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this enum into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        buffer.write(self.value.to_bytes(1, "little"))

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "CarRecordType":
        """
        Read binary data from a buffer and parse it into an object.

        :param buffer: The buffer from which to read.
        :return: The parsed object.
        """
        val = int.from_bytes(buffer.read(1), "little")
        return CarRecordType(val)
