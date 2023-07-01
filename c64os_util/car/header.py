import datetime
import typing

from ..util import LC_CODEC
from .common import CarArchiveType


class ArchiveTimestamp:
    def __init__(
        self,
        year: int = 1900,
        month: int = 0,
        day: int = 0,
        hour: int = 0,
        minute: int = 0,
    ):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, value: int):
        self._year = value

    @property
    def month(self) -> int:
        return self._month

    @month.setter
    def month(self, value: int):
        self._month = value

    @property
    def day(self) -> int:
        return self._day

    @day.setter
    def day(self, value: int):
        self._day = value

    @property
    def hour(self) -> int:
        return self._hour

    @hour.setter
    def hour(self, value: int):
        self._hour = value

    @property
    def minute(self) -> int:
        return self._minute

    @minute.setter
    def minute(self, value: int):
        self._minute = value

    @staticmethod
    def from_datetime(timestamp: datetime.datetime) -> "ArchiveTimestamp":
        return ArchiveTimestamp(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=timestamp.hour,
            minute=timestamp.minute,
        )

    def to_datetime(self) -> datetime.datetime:
        return datetime.datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
        )

    def serialize(self, buffer: typing.BinaryIO):
        values = [self.year - 1900, self.month, self.day, self.hour, self.minute]
        for value in values:
            buffer.write(value.to_bytes(1, "little"))

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "ArchiveTimestamp":
        fields = ["year", "month", "day", "hour", "minute"]
        values = buffer.read(len(fields))
        d = dict(zip(fields, values))
        d["year"] += 1900
        return ArchiveTimestamp(**d)


class ArchiveHeader:
    MAX_NOTE_SIZE = 31
    CAR_MAGIC = "C64Archive"
    CAR_VERSION = 2

    def __init__(
        self,
        archive_type: CarArchiveType = CarArchiveType.GENERAL,
        timestamp: datetime.datetime = datetime.datetime.utcnow(),
        note: str = "",
    ):
        assert len(note) <= ArchiveHeader.MAX_NOTE_SIZE
        self.archive_type = archive_type
        self.timestamp = ArchiveTimestamp.from_datetime(timestamp)
        self.note = note

    @property
    def archive_type(self) -> CarArchiveType:
        return self._archive_type

    @archive_type.setter
    def archive_type(self, value: CarArchiveType):
        self._archive_type = value

    @property
    def timestamp(self) -> ArchiveTimestamp:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: ArchiveTimestamp):
        self._timestamp = value

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, value: str):
        self._note = value

    def serialize(self, buffer: typing.BinaryIO):
        self.archive_type.serialize(buffer)
        buffer.write(ArchiveHeader.CAR_MAGIC.encode(LC_CODEC))
        buffer.write(ArchiveHeader.CAR_VERSION.to_bytes(1, "little"))
        self.timestamp.serialize(buffer)
        note_bytes = self.note.encode(LC_CODEC)
        note_bytes = note_bytes.ljust(ArchiveHeader.MAX_NOTE_SIZE, b"\0")
        buffer.write(note_bytes)

    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> "ArchiveHeader":
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
