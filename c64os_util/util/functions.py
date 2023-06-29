import os


def copy_buffer(src, dest, src_whence=os.SEEK_CUR, src_seek=0, dest_whence=os.SEEK_CUR, dest_seek=0, max_size=-1, chunk_size=1024):
    src.seek(src_seek, src_whence)
    dest.seek(dest_seek, dest_whence)
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