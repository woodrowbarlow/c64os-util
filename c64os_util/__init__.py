"""
The ``c64os_util`` package provides a collection of classes, methods, and scripts that
allow you to parse, generate, or manipulate certain types of files that are used in
C64 OS. This package is useful to developers who are cross-assembling C64 OS
applications and wish to package up their resources as part of the build pipeline.

`C64 OS <https://c64os.com/>`_ is an operating system designed for the Commodore 64
designed by Gregory Nacu and released in 2022. It provides a rich graphical toolkit,
customizeable launcher, peripheral drivers, multimedia formats, a collection of
utilities and applications, and more.

At the moment, the main functionality provided by this package is the ability to
read and write C64 Archive (``.car``) files. Future plans includes support for the
various multimedia formats.
"""

from .car import C64Archive, CarArchiveType, CarCompressionType, CarRecordType
from .util import LC_CODEC, UC_CODEC
