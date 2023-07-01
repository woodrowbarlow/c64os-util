"""
Classes and methods related to the archive header.
"""

import datetime
import typing

from ..util import LC_CODEC
from .common import CarArchiveType


class ArchiveTimestamp:  # pylint: disable=R0902
    """
    Archives contain a creation timestamp which is precise to the minute. This class
    represents an archive timestamp.
    """

    def __init__(  # pylint: disable=R0913
        self,
        year: int = 1900,
        month: int = 0,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
    ):
        """
        Create a new timestamp object.
        :param year: The year.
        :param month: The month.
        :param day: The day.
        :param hour: The hour.
        :param minute: The minute.
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

    @property
    def year(self) -> int:
        """
        Get the timestamp year.
        :return: The year.
        """
        return self._year

    @year.setter
    def year(self, value: int):
        """
        Set the timestamp year.
        :param value: The new year.
        """
        self._year = value

    @property
    def month(self) -> int:
        """
        Get the timestamp month.
        :return: The month.
        """
        return self._month

    @month.setter
    def month(self, value: int):
        """
        Set the timestamp month.
        :param value: The new month.
        """
        self._month = value

    @property
    def day(self) -> int:
        """
        Get the timestamp day.
        :return: The day.
        """
        return self._day

    @day.setter
    def day(self, value: int):
        """
        Set the timestamp day.
        :param value: The new day.
        """
        self._day = value

    @property
    def hour(self) -> int:
        """
        Get the timestamp hour.
        :return: The hour.
        """
        return self._hour

    @hour.setter
    def hour(self, value: int):
        """
        Set the timestamp hour.
        :param value: The new hour.
        """
        self._hour = value

    @property
    def minute(self) -> int:
        """
        Get the timestamp minute.
        :return: The minute.
        """
        return self._minute

    @minute.setter
    def minute(self, value: int):
        """
        Set the timestamp minute.
        :param value: The new minute.
        """
        self._minute = value

    @staticmethod
    def from_datetime(timestamp: datetime.datetime) -> "ArchiveTimestamp":
        """
        Create a timestamp object from a standard datetime object.
        (Note the precision will not include seconds.)
        :param timestamp: The datetime formatted timestamp object.
        :return: The archive timestamp.
        """
        return ArchiveTimestamp(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=timestamp.hour,
            minute=timestamp.minute,
        )

    def to_datetime(self) -> datetime.datetime:
        """
        Convert this to a standard datetime object.
        (Note the precision will not include seconds.)
        :return: A datetime formatted timestamp object.
        """
        return datetime.datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
        )

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this timestamp into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        values = [self.year - 1900, self.month, self.day, self.hour, self.minute]
        for value in values:
            buffer.write(value.to_bytes(1, "little"))

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "ArchiveTimestamp":
        """
        Read binary data from a buffer and parse it into a timestamp object.

        :param header: The header (parsed from the buffer already).
        :param buffer: The buffer from which to read.
        :return: The parsed timestamp object.
        """
        fields = ["year", "month", "day", "hour", "minute"]
        values = buffer.read(len(fields))
        kwargs = dict(zip(fields, values))
        kwargs["year"] += 1900
        return ArchiveTimestamp(**kwargs)


class ArchiveHeader:
    """
    The archive header contains some metadata about the file. This class provides
    properties to read and write that metadata.
    """

    MAX_NOTE_SIZE = 31
    CAR_MAGIC = "C64Archive"
    CAR_VERSION = 2

    def __init__(
        self,
        archive_type: CarArchiveType = CarArchiveType.GENERAL,
        timestamp: datetime.datetime = datetime.datetime.utcnow(),
        note: str = "",
    ):
        """
        Create a new archive header object.

        :param archive_type: The type of archive to create.
        :param timestamp: The archive creation timestamp.
        :param note: A message to store in the archive 'note' field.
        """
        assert len(note) <= ArchiveHeader.MAX_NOTE_SIZE
        self.archive_type = archive_type
        self.timestamp = ArchiveTimestamp.from_datetime(timestamp)
        self.note = note

    @property
    def archive_type(self) -> CarArchiveType:
        """
        Get the archive type.
        :return: The archive type.
        """
        return self._archive_type

    @archive_type.setter
    def archive_type(self, value: CarArchiveType):
        """
        Set the archive type.
        :param value: The new archive type.
        """
        self._archive_type = value

    @property
    def timestamp(self) -> ArchiveTimestamp:
        """
        Get the timestamp.
        :return: The timestamp.
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: ArchiveTimestamp):
        """
        Set the timestamp.
        :param value: The new timestamp.
        """
        self._timestamp = value

    @property
    def note(self) -> str:
        """
        Get the note.
        :return: The note.
        """
        return self._note

    @note.setter
    def note(self, value: str):
        """
        Set the note.
        :param value: The new note.
        """
        self._note = value

    def serialize(self, buffer: typing.BinaryIO):
        """
        Convert this header into binary data and write it to a buffer.

        :param buffer: The buffer into which to write.
        """
        self.archive_type.serialize(buffer)
        buffer.write(ArchiveHeader.CAR_MAGIC.encode(LC_CODEC))
        buffer.write(ArchiveHeader.CAR_VERSION.to_bytes(1, "little"))
        self.timestamp.serialize(buffer)
        note_bytes = self.note.encode(LC_CODEC)
        note_bytes = note_bytes.ljust(ArchiveHeader.MAX_NOTE_SIZE, b"\0")
        buffer.write(note_bytes)

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "ArchiveHeader":
        """
        Read binary data from a buffer and parse it into a header object.

        :param header: The header (parsed from the buffer already).
        :param buffer: The buffer from which to read.
        :return: The parsed header object.
        """
        archive_type = CarArchiveType.deserialize(buffer)
        magic = buffer.read(10).decode(LC_CODEC)
        version = int.from_bytes(buffer.read(1), "little")
        timestamp = ArchiveTimestamp.deserialize(buffer)
        note_buff = buffer.read(ArchiveHeader.MAX_NOTE_SIZE)
        note = note_buff.rstrip(b"\0").decode(LC_CODEC)
        assert magic == ArchiveHeader.CAR_MAGIC
        assert version == ArchiveHeader.CAR_VERSION
        return ArchiveHeader(
            archive_type=archive_type, timestamp=timestamp.to_datetime(), note=note
        )
