import sortedcollections

from c64os_util.schema.util import BaseSchema, LC_CODEC, read_line


class ApplicationMenuEntry:

    def __init__(self, name, modifier_keys, action_key, action_msg):
        self.name = name
        self.modifier_keys = modifier_keys
        self.action_key = action_key
        self.action_msg = action_msg


    def _serialize(self):
        val = f'{str(self.modifier_keys)}{self.action_key}{self.action_msg}'
        return f'{self.name}:{val}\r'.encode(LC_CODEC)


    @staticmethod
    def _deserialize(line):
        sep = line.find(':')
        name = line[:sep]
        val = line[sep+1:]
        assert len(val) == 3
        mod = int(val[0])
        key = val[1]
        msg = val[2]
        return ApplicationMenuEntry(name, mod, key, msg)


class ApplicationMenu(BaseSchema, sortedcollections.OrderedSet):

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


    def serialize(self, buffer):
        self._serialize(buffer)
        buffer.write('\r'.encode(LC_CODEC))


    def _serialize(self, buffer):
        count = chr(ord('a') + len(self) - 1)
        buffer.write(f'{self.name};{count}\r'.encode(LC_CODEC))
        for child in self:
            buffer.write(child._serialize())


    @staticmethod
    def deserialize(buffer):
        line = read_line(buffer)
        sep = line.find(';')
        sep_file = line.find(':')
        if sep_file > 0:
            if sep < 0 or sep_file < sep:
                return ApplicationMenuEntry._deserialize(line)
        name = line[:sep]
        count = ord(line[sep+1:]) - ord('a') + 1
        inst = ApplicationMenu(name)
        for _ in range(count):
            inst.add(ApplicationMenu.deserialize(buffer))
        return inst
