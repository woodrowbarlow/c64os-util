import abc


LC_CODEC = 'petscii_c64en_lc'
UC_CODEC = 'petscii_c64en_uc'


def read_until(buffer, until):
    assert len(until) == 1
    s = b''
    while True:
        c = buffer.read(1)
        if not c:
            break
        s += c
        if c == until:
            break
    return s


def read_line(buffer, decode=True, strip_eol=True, eol='\r', codec=LC_CODEC):
    eol_bytes = eol.encode(codec)
    line = read_until(buffer, eol_bytes)
    if strip_eol:
        line = line.rstrip(eol_bytes)
    if decode:
        line = line.decode(codec)
    return line



class BaseSchema(abc.ABC):

    def serialize(self, buffer):
        raise NotImplementedError()


    @staticmethod
    def deserialize(self, buffer):
        raise NotImplementedError()
