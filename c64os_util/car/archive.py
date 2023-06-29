import datetime
import typing

from .common import CarArchiveType
from .header import ArchiveHeader
from .record import ArchiveRecord
from ..util import LC_CODEC


class C64Archive:

    def __init__(
        self, archive_type: CarArchiveType = CarArchiveType.GENERAL,
        timestamp: datetime.datetime = datetime.datetime.utcnow(), note: str = ''
    ):
        self.header = ArchiveHeader(archive_type=archive_type, timestamp=timestamp, note=note)
        self.root = None


    @property
    def header(self) -> ArchiveHeader:
        return self._header


    @header.setter
    def header(self, value: ArchiveHeader):
        self._header = value


    @property
    def root(self) -> ArchiveRecord:
        return self._root


    @root.setter
    def root(self, value: ArchiveRecord):
        self._root = value


    def serialize(self, buffer: typing.BinaryIO):
        self.header.serialize(buffer)
        if self.root is not None:
            self.root.serialize(buffer)


    @staticmethod
    def deserialize(buffer: typing.BinaryIO) -> 'C64Archive':
        header = ArchiveHeader.deserialize(buffer)
        archive = C64Archive(
            archive_type=header.archive_type,
            timestamp=header.timestamp.to_datetime(),
            note=header.note,
        )
        archive.root = ArchiveRecord.deserialize(buffer)
        return archive
