import abc
import os
import io
import sortedcollections

from c64os_util.schema.util import BaseSchema, LC_CODEC, read_line
from c64os_util.schema.car.common import CarRecordType, CarCompressionType


class ArchiveRecordHeader(BaseSchema):

    MAX_NAME_SIZE = 15


    def __init__(self, record_type, size, name, compression_type):
        self.record_type = record_type
        self.size = size
        self.name = name
        self.compression_type = compression_type


    def serialize(self, buffer):
        self.record_type.serialize(buffer)
        buffer.write(b'\0') # lock byte?
        size_bytes = self.size.to_bytes(3, 'little')
        buffer.write(size_bytes)
        name_bytes = self.name.encode(LC_CODEC)
        name_bytes = name_bytes.ljust(ArchiveRecordHeader.MAX_NAME_SIZE, b'\xA0')
        buffer.write(name_bytes)
        buffer.write(b'\0') # ???
        self.compression_type.serialize(buffer)


    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.record_type != other.record_type:
            return False
        return True


class ArchiveRecord(BaseSchema, abc.ABC):

    @property
    def parent(self):
        raise NotImplementedError()


    @property
    def header(self):
        raise NotImplementedError()


    @property
    def name(self):
        return self.header.name


    @property
    def record_type(self):
        return self.header.record_type


    @property
    def compression_type(self):
        return self.header.compression_type


    def path(self, sep=os.path.sep):
        path = []
        record = self
        while record:
            path.insert(0, record.header.name)
            record = record.parent
        return sep.join(path)


    def __eq__(self, other):
        return self.header == other.header


    @staticmethod
    def deseralize(buffer):
        header = ArchiveHeader.deseralize(buffer)
        return ArchiveRecord.deseralize(buffer, header)


    @staticmethod
    def deserialize(buffer, header):
        if child_header.record_type == CarRecordType.DIRECTORY:
            child = ArchiveDirectoryRecord.deserialize(buffer, child_header)
        else:
            child = ArchiveFileRecord.deserialize(buffer, child_header)


class ArchiveFileRecord(ArchiveRecord, io.BytesIO):

    def __init__(self, name, file_type, compression_type, *args, **kwargs):
        if file_type == CarRecordType.DIRECTORY:
            raise ValueError("file nodes cannot be directories")
        if compression_type != CarCompressionType.NONE:
            raise ValueError("compression is not supported yet")
        self._parent = None
        self._header = ArchiveRecordHeader(
            file_type, 0, name, compression_type
        )
        super().__init__(*args, **kwargs)
        self._update_size()


    @property
    def header(self):
        return self._header


    @property
    def parent(self):
        return self._parent


    def _update_size(self):
        self.header.size = self.getbuffer().nbytes


    def truncate(self, size=None):
        super().truncate(size=size)
        self._update_size()


    def write(self, data):
        super().write(data)
        self._update_size()


    def serialize(self, buffer):
        self.header.serialize(buffer)
        while True:
            chunk = self.read(1024)
            if not chunk:
                break
            buffer.write(chunk)


    @staticmethod
    def deseralize(buffer, header):
        record = ArchiveFileRecord(
            header.name, header.record_type,
            header.compression_type,
        )
        size = header.size
        while size:
            chunk = buffer.read(1024)
            if not chunk:
                break
            record.write(chunk)
            size -= len(chunk)
        record.seek(0)


class ArchiveDirectoryRecord(ArchiveRecord, sortedcollections.OrderedSet):

    def __init__(self, name, *args, **kwargs):
        self._parent = None
        self._header = ArchiveRecordHeader(
            CarRecordType.DIRECTORY,
            0, name,
            CarCompressionType.NONE
        )
        super().__init__(*args, **kwargs)


    @property
    def header(self):
        return self._header


    @property
    def parent(self):
        return self._parent


    def directories(self):
        for child in self:
            if not isinstance(child, ArchiveDirectoryRecord):
                continue
            yield child


    def files(self):
        for child in self:
            if isinstance(child, ArchiveDirectoryRecord):
                continue
            yield child


    def add(self, *args, **kwargs):
        super().add(*args, **kwargs)
        self.header.size = len(self)
        for child in self:
            child._parent = self


    def discard(self, *args, **kwargs):
        super().discard(*args, **kwargs)
        self.header.size = len(self)
        for child in self:
            child._parent = self


    def get_child(self, name):
        for child in self:
            if child.header.name == name:
                return child
        return None


    def walk(self):
        yield self
        for dir in self.directories():
            yield from dir.walk()


    def serialize(self, buffer):
        self.header.serialize(buffer)
        for child in self:
            child.serialize(buffer)


    @staticmethod
    def deserialize(buffer, header):
        record = ArchiveDirectoryRecord(header.name)
        for _ in range(header.size):
            child_header = ArchiveRecordHeader.deserialize(buffer)
            child = ArchiveRecord.deserialize(buffer, child_header)
            record.add(child)
        return record
