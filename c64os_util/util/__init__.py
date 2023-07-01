import codecs
import typing

from .codec import CODEC_INFOS, LC_CODEC, UC_CODEC
from .functions import copy_buffer


def petscii_search_fn(encoding: str) -> typing.Optional[codecs.CodecInfo]:
    return CODEC_INFOS.get(encoding, None)


codecs.register(petscii_search_fn)
