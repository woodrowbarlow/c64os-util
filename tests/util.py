def cmp_buffers(f1, f2):
    while True:
        b1 = f1.read(1024)
        b2 = f2.read(1024)
        if b1 != b2:
            return False
        if not b1:
            break
    return True
