import enum


class CarArchiveType(enum.Enum):

    GENERAL = 0
    RESTORE = 1
    INSTALL = 2


    def serialize(self, buffer):
        return self.value.to_bytes(1, 'little')


    @staticmethod
    def deserialize(buffer):
        val = int.from_bytes(buffer.read(1), 'little')
        return CarRecordType(val)


class CarCompressionType(enum.Enum):

    NONE = 0
    RLE = 1
    LZ = 2


    def serialize(self, buffer):
        return self.value.to_bytes(1, 'little')


    @staticmethod
    def deserialize(buffer):
        val = int.from_bytes(buffer.read(1), 'little')
        return CarRecordType(val)


class CarRecordType(enum.Enum):

    PRGFILE = 0x50
    SEQFILE = 0x53
    DIRECTORY = 0x44


    def is_directory(self):
        return self == CarRecordType.DIRECTORY


    def serialize(self, buffer):
        return self.value.to_bytes(1, 'little')


    @staticmethod
    def deserialize(buffer):
        val = int.from_bytes(buffer.read(1), 'little')
        return CarRecordType(val)
