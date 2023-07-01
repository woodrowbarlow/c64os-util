"""
Each record (file or directory) within the archive is represented using classes within
this module. The base class is called ``ArchiveRecord`` and the derived classes are
``ArchiveFile`` and ``ArchiveDirectory``.

Just as on a typical filesystem, the records form a tree structure (because directories
can have children). There are some requirements; mostly, you can't have more than one
record of the same name in a single place.
"""

from .record import ArchiveDirectory, ArchiveFile, ArchiveRecord
