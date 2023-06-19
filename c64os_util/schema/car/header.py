import datetime

from c64os_util.schema.util import BaseSchema, LC_CODEC, read_line
from c64os_util.schema.car.common import CAR_MAGIC, CAR_VERSION, CarArchiveType


class ArchiveTimestamp(BaseSchema):

    def __init__(self, year=1900, month=0, day=0, hour=0, minute=0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute


    @staticmethod
    def from_datetime(timestamp):
        return ArchiveTimestamp(
            year=timestamp.year, month=timestamp.month, day=timestamp.day,
            hour=timestamp.hour, minute=timestamp.minute,
        )


    @property
    def datetime(self):
        return datetime.datetime(
            year=self.year, month=self.month, day=self.day,
            hour=self.hour, minute=self.minute,
        )


    def serialize(self, buffer):
        values = [ self.year - 1900, self.month, self.day, self.hour, self.minute ]
        for value in values:
            buffer.write(value.to_bytes(1, 'little'))


    @staticmethod
    def deserialize(buffer):
        fields = ['year', 'month', 'day', 'hour', 'minute']
        values = buffer.read(len(fields))
        d = dict(zip(fields, values))
        d['year'] += 1900
        return ArchiveTimestamp(**d)


class ArchiveHeader(BaseSchema):

    MAX_NOTE_SIZE = 31


    def __init__(
        self, archive_type=CarArchiveType.GENERAL,
        timestamp=datetime.datetime.utcnow(), note=''
    ):
        assert len(note) <= ArchiveHeader.MAX_NOTE_SIZE
        self.archive_type = archive_type
        self._timestamp = ArchiveTimestamp.from_datetime(timestamp)
        self.note = note


    @property
    def timestamp(self):
        return self._timestamp


    def serialize(self, buffer):
        buffer.write(self.archive_type.value.to_bytes(1, 'little'))
        buffer.write(CAR_MAGIC.encode(LC_CODEC))
        buffer.write(CAR_VERSION.to_bytes(1, 'little'))
        self.timestamp.serialize(buffer)
        buffer.write(self.note.encode(LC_CODEC).ljust(ArchiveHeader.MAX_NOTE_SIZE))


    @staticmethod
    def deserialize(buffer):
        a_type = int.from_bytes(buffer.read(1), 'little')
        archive_type = CarArchiveType(a_type)
        magic = buffer.read(10).decode(LC_CODEC)
        version = int.from_bytes(buffer.read(1), 'little')
        timestamp = ArchiveTimestamp.deserialize(buffer)
        note_buff = buffer.read(ArchiveHeader.MAX_NOTE_SIZE)
        note = note_buff.rstrip(b'\0').decode(LC_CODEC)
        assert magic == CAR_MAGIC
        assert version == CAR_VERSION
        return ArchiveHeader(archive_type=archive_type, timestamp=timestamp, note=note)
