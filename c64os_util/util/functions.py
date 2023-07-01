"""
Utility functions (used throughout the project).
"""


def copy_buffer(
    src,
    dest,
    max_size=-1,
    chunk_size=1024,
):
    """
    Copy the contents of the ``src`` buffer into the ``dest`` buffer.
    :param src: The source buffer.
    :param dest: The destination buffer.
    :param max_size: The maximum number of bytes to copy from ``src``.
    :param chunk_size: The maximum number of bytes to copy at once.
    """
    count = 0
    while True:
        size = chunk_size
        if max_size >= 0:
            size = min(max_size - count, size)
        chunk = src.read(size)
        if not chunk:
            break
        dest.write(chunk)
        count += len(chunk)
