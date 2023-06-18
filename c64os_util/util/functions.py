def copy_buffer(
    src,
    dest,
    max_size=-1,
    chunk_size=1024,
):
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
