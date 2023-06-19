import contextlib
import datetime
import os

from c64os_util.schema.util import BaseSchema, LC_CODEC
from c64os_util.schema.car.record import ArchiveDirectoryRecord, ArchiveFileRecord
from c64os_util.schema.car.header import ArchiveHeader
from c64os_util.schema.car.common import (
    CarArchiveType, CarRecordType, CarCompressionType,
)


class ArchiveIterator:

    def __init__(self, start):
        self.records = []
        if isinstance(start, ArchiveDirectoryRecord):
            for record in start.walk():
                self.records += list(record.files())
        else:
            self.records.append(start)
        self.idx = 0


    def __next__(self):
        if self.idx >= len(self.records):
            raise StopIteration
        idx = self.idx
        self.idx += 1
        return self.records[idx]


class CbmArchive(BaseSchema):

    def __init__(
        self, archive_type=CarArchiveType.GENERAL,
        timestamp=datetime.datetime.utcnow(), note='',
        root=None
    ):
        self._header = ArchiveHeader(
            archive_type, timestamp, note
        )
        self._root = root


    @property
    def header(self):
        return self._header


    @property
    def root(self):
        return self._root


    def ls(self, path, sep=os.path.sep):
        if self.root is None:
            raise FileNotFoundError()
        parts = path.split(sep)
        if not parts:
            raise FileNotFoundError()
        return self._ls(self.root, parts[0], parts[1:])


    def _ls(self, record, name, parts):
        if record.name != name:
            raise FileNotFoundError()
        if not parts:
            return record
        if not isinstance(record, ArchiveDirectoryRecord):
            raise FileNotFoundError()
        name = parts[0]
        parts = parts[1:]
        for child in record:
            if child.name == name:
                return self._ls(child, name, parts)
        raise FileNotFoundError()


    def rm(self, path, sep=os.path.sep, recursive=False):
        record = self.ls(path, sep=sep)
        if not recursive:
            if isinstance(record, ArchiveDirectoryRecord) and len(record):
                raise ValueError("directory is not empty")
        record.parent.remove(record)


    def mkdir(self, path, sep=os.path.sep, create_missing=False):
        parts = path.split(sep)
        if not parts:
            raise ValueError('invalid path')
        self._root = self._mkdir(self.root, parts[0], parts[1:], create_missing)


    def _mkdir(self, record, name, parts, create_missing):
        if record is None:
            if parts and not create_missing:
                raise FileNotFoundError()
            record = ArchiveDirectoryRecord(name)
        if record.name != name:
            raise ValueError('cannot have more than one root')
        if not parts:
            return record
        name = parts[0]
        parts = parts[1:]
        child = record.get_child(name)
        child = self._mkdir(child, name, parts, create_missing)
        record.append(child)
        return record


    def touch(
        self, path, file_type=CarRecordType.SEQFILE,
        compression_type=CarCompressionType.NONE,
        sep=os.path.sep, create_directories=False
    ):
        parts = path.split(sep)
        if not parts:
            raise ValueError('invalid path')
        parent_path = sep.join(parts[:-1])
        name = parts[-1]
        if create_directories:
            self.mkdir(parent_path, sep=sep, create_missing=True)
        parent = None
        if parent_path:
            parent = self.ls(parent_path, sep=sep)
        child = ArchiveFileRecord(name, file_type, compression_type)
        if parent is not None:
            parent.append(child)
        else:
            self._root = child


    def __iter__(self):
        return ArchiveIterator(self.root)


    @contextlib.contextmanager
    def __call__(self, path, mode='r', sep=os.path.sep, encoding=None, errors=None, newline=None, file_type=None, compression_type=None):
        """
        open a file inside the archive for reading or writing.

        mode is an optional string that specifies the mode in which the file
        is opened. It defaults to 'r' which means open for reading in text
        mode.  Other common values are 'w' for writing (truncating the file if
        it already exists), 'x' for creating and writing to a new file, and
        'a' for appending.
        In text mode, if encoding is not specified the encoding defaults to
        'petscii_c64en_lc'. (For reading and writing raw bytes use binary mode
        and leave encoding unspecified.) The available modes are:

        ========= ===============================================================
        Character Meaning
        --------- ---------------------------------------------------------------
        'r'       open for reading (default)
        'w'       open for writing, truncating the file first
        'x'       create a new file and open it for writing
        'a'       open for writing, appending to the end of the file if it exists
        'b'       binary mode
        't'       text mode (default)
        '+'       open a disk file for updating (reading and writing)
        ========= ===============================================================

        The default mode is 'r' (open for reading text). For binary random
        access, the mode 'w+b' opens and truncates the file to 0 bytes, while
        'r+b' opens the file without truncation. The 'x' mode implies 'w' and
        raises an `FileExistsError` if the file already exists.

        encoding is the name of the encoding used to decode or encode the
        file. This should only be used in text mode. The default encoding is
        'petscii_c64en_lc', but any encoding supported by Python can be
        passed.  See the codecs and cbmcodecs2 modules for the list of
        supported encodings.

        file_type is used when creating files. it should not be specified
        when reading files. the default record type is SEQFILE.

        open() returns a file object whose type depends on the mode, and
        through which the standard file operations such as reading and writing
        are performed. When open() is used to open a file in a text mode ('w',
        'r', 'wt', 'rt', etc.), it returns a TextIOWrapper. When used to open
        a file in a binary mode, the returned class varies: in read binary
        mode, it returns a BufferedReader; in write binary and append binary
        modes, it returns a BufferedWriter, and in read/write mode, it returns
        a BufferedRandom.
        """

        m = self._decode_mode(mode)
        if m['creating'] or m['writing'] or m['appending']:
            if m['creating']:
                record = self.ls(path, sep=sep)
                if record:
                    raise ValueError(f"path {path} already exists")
            if file_type is None:
                file_type = CarRecordType.SEQFILE
            if compression_type is None:
                compression_type = CarCompressionType.NONE
            self.touch(path, sep=sep, file_type=file_type)
        else:
            if file_type is not None:
                raise ValueError("file_type is invalid for reading")
            if compression_type is not None:
                raise ValueError("compression_type is invalid for reading")
        if m['binary']:
            if encoding is not None:
                raise ValueError("encoding is invalid for binary mode")
            if newline is not None:
                raise ValueError("newline is invalid for binary mode")

        if encoding is None:
            encoding = LC_CODEC
        if newline is None:
            newline = '\r'

        record = self.ls(path, sep=sep)
        if m['appending']:
            record.seek(0, os.SEEK_END)
        else:
            record.seek(0, os.SEEK_SET)
        if m['writing']:
            record.truncate()

        if m['text']:
            buffer = io.TextIOWrapper(
                record, encoding=encoding, errors=errors, newline=newline
            )
        else:
            if m['reading']:
                buffer = io.BufferedReader(record)
            elif m['writing']:
                buffer = io.BufferedWriter(record)
            elif m['updating']:
                buffer = io.BufferedRandom(record)

        try:
            yield buffer
        finally:
            buffer.flush()


    def _decode_mode(self, mode):
        creating = False
        reading = False
        writing = False
        appending = False
        updating = False
        text = False
        binary = False
        for i in range(len(mode)):
            c = mode[i]
            if c == 'x':
                creating = True
            elif c == 'r':
                reading = True
            elif c == 'w':
                writing = True
            elif c == 'a':
                appending = True
            elif c == '+':
                updating = True
            elif c == 't':
                text = True
            elif c == 'b':
                binary = True
            else:
                raise ValueError(f"invalid mode (unrecognized {c})")
            if c in mode[i+1:]:
                raise ValueError(f"invalid mode (duplicate {c})")
        if text and binary:
            raise ValueError(f"invalid mode (text and binary)")
        if not text and not binary:
            text = True
        actions = [ creating, reading, writing, appending ]
        actions = [ action for action in actions if action ]
        if len(actions) != 1:
            raise ValueError(f"invalid mode (need one of r/w/x/a)")
        return {
            'creating': creating,
            'reading': reading,
            'writing': writing,
            'appending': appending,
            'updating': updating,
            'text': text,
            'binary': binary,
        }


    def serialize(self, buffer):
        self.header.serialize(buffer)
        if self.root:
            self.root.serialize(buffer)


    @staticmethod
    def deserialize(buffer):
        header = ArchiveHeader.deseralize(buffer)
        root = ArchiveRecord.deseralize(buffer)
        return CbmArchive(
            archive_type=header.archive_type,
            timestamp=header.timestamp.datetime,
            note=header.note, root=root
        )


def load_car(path):
    with open(path, 'rb') as f:
        return CbmArchive.deseralize(f)


def save_car(archive, path):
    with open(path, 'wb') as f:
        archive.serialize(f)
