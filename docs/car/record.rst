Archive Records
===============

An ``ArchiveRecord`` represents something that is inside the archive: either a file, or a directory. Every archive has a single root record (possibly containing other records, if it is a directory).

Records are serialized and de-serialized recursively -- performing either operation on the root node will operate on the entire file tree.

De-serializing should be done using the base class, ``ArchiveRecord``: ::

    record = ArchiveRecord.deserialize(buffer)

This will return an instance of a derived class, either ``ArchiveDirectory`` or ``ArchiveFile``.

The ``ArchiveDirectory`` class is basically just a named list. The directory itself has a name, and it has children (which might be files or other directories), each of which have a name.

The ``ArchiveFile`` class is basically just a named, seekable binary buffer. It can be read from and written to directly (although usually you would use the higher-level functions to open it in certain modes).

Both of these derived classes can also be instantiated manually. For instance: ::

    record = ArchiveDirectory(name='root')
    # can append or extend children like a normal list
    record += [
        ArchiveDirectory(name='foo'),
        ArchiveFile(name='bar', file_type=CarRecordType.PRGFILE),
    ]
    # can reference children by their index:
    f = record[0]
    # or dict-style by the child's name:
    f = record['bar']
    # files can be read from and written to
    f.write(b'\0')
    f.seek(0)
    data = f.read()

And both derived classes can serialize back to binary data: ::

    record.serialize(buffer)

.. toctree::
   :titlesonly:

   record/file
   record/directory
   record/record
   record/header


