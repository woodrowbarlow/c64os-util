"""
Internal utilities used throughout the project.
"""

import codecs
import typing

from .codec import CODEC_INFOS, LC_CODEC, UC_CODEC
from .functions import copy_buffer


def petscii_search_fn(encoding: str) -> typing.Optional[codecs.CodecInfo]:
    """
    Search for PETSCII-related encodings.
    :param encoding: The encoding name.
    :return: A CodecInfo object (or None).
    """
    return CODEC_INFOS.get(encoding, None)


codecs.register(petscii_search_fn)
