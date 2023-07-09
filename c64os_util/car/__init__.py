"""
Classes and methods related to C64 Archive (``.car``) files.
"""

import shutil

from .archive import C64Archive, load_car, pack_car, save_car, unpack_car
from .common import CarArchiveType, CarCompressionType, CarRecordType
from .record import ArchiveDirectory, ArchiveFile, ArchiveRecord

shutil.register_archive_format(
    "car", pack_car, description="uncompressed C64 Archive (c64os-util)"
)
shutil.register_unpack_format(
    "car", [], unpack_car, description="uncompressed C64 Archive (c64os-util)"
)
