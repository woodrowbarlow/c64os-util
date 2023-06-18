from c64os_util.schema.util import BaseSchema, LC_CODEC, read_line

class ApplicationMetadata(BaseSchema):

    def __init__(self, name, version, year, author):
        self.name = name
        self.version = version
        self.year = year
        self.author = author


    def serialize(self, buffer):
        buffer.write(f'{self.name}\r'.encode(LC_CODEC))
        buffer.write(b'\x20' + f'{self.version}\r'.encode(LC_CODEC))
        buffer.write(f'{self.year}\r'.encode(LC_CODEC))
        buffer.write(f'{self.author}\r'.encode(LC_CODEC))


    @staticmethod
    def deserialize(buffer):
        name = read_line(buffer)
        buffer.read(1)
        version = read_line(buffer)
        year_s = read_line(buffer)
        year = int(year_s)
        author = read_line(buffer)
        return ApplicationMetadata(name, version, year, author)
