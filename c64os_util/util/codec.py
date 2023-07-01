"""
Implementation details for the PETSCII text codec.
"""

import codecs
import typing

LC_CODEC = "petscii_c64en_lc"
UC_CODEC = "petscii_c64en_uc"

# charmaps generated from:
# http://www.df.lth.se/~triad/krad/recode/petscii.html

LC_CHARMAP = (
    "\uFFFE\uFFFE\uFFFE\uFFFE\uFFFE\uF100\uFFFE\uFFFE"
    "\uF118\uF119\uFFFE\uFFFE\uFFFE\u000D\u000E\uFFFE"
    "\uFFFE\uF11C\uF11A\uF120\u007F\uFFFE\uFFFE\uFFFE"
    "\uFFFE\uFFFE\uFFFE\uFFFE\uF101\uF11D\uF102\uF103"
    "\u0020\u0021\u0022\u0023\u0024\u0025\u0026\u0027"
    "\u0028\u0029\u002A\u002B\u002C\u002D\u002E\u002F"
    "\u0030\u0031\u0032\u0033\u0034\u0035\u0036\u0037"
    "\u0038\u0039\u003A\u003B\u003C\u003D\u003E\u003F"
    "\u0040\u0061\u0062\u0063\u0064\u0065\u0066\u0067"
    "\u0068\u0069\u006A\u006B\u006C\u006D\u006E\u006F"
    "\u0070\u0071\u0072\u0073\u0074\u0075\u0076\u0077"
    "\u0078\u0079\u007A\u005B\u00A3\u005D\u2191\u2190"
    "\u2501\u0041\u0042\u0043\u0044\u0045\u0046\u0047"
    "\u0048\u0049\u004A\u004B\u004C\u004D\u004E\u004F"
    "\u0050\u0051\u0052\u0053\u0054\u0055\u0056\u0057"
    "\u0058\u0059\u005A\u253C\uF12E\u2502\u2592\uF139"
    "\uFFFE\uF104\uFFFE\uFFFE\uFFFE\uF110\uF112\uF114"
    "\uF116\uF111\uF113\uF115\uF117\u000A\u000F\uFFFE"
    "\uF105\uF11E\uF11B\u000C\uF121\uF106\uF107\uF108"
    "\uF109\uF10A\uF10B\uF10C\uF10D\uF11D\uF10E\uF10F"
    "\u00A0\u258C\u2584\u2594\u2581\u258F\u2592\u2595"
    "\uF12F\uF13A\uF130\u251C\uF134\u2514\u2510\u2582"
    "\u250C\u2534\u252C\u2524\u258E\u258D\uF131\uF132"
    "\uF133\u2583\u2713\uF135\uF136\u2518\uF137\uF138"
    "\u2501\u0041\u0042\u0043\u0044\u0045\u0046\u0047"
    "\u0048\u0049\u004A\u004B\u004C\u004D\u004E\u004F"
    "\u0050\u0051\u0052\u0053\u0054\u0055\u0056\u0057"
    "\u0058\u0059\u005A\u253C\uF12E\u2502\u2592\uF139"
    "\u00A0\u258C\u2584\u2594\u2581\u258F\u2592\u2595"
    "\uF12F\uF13A\uF130\u251C\uF134\u2514\u2510\u2582"
    "\u250C\u2534\u252C\u2524\u258E\u258D\uF131\uF132"
    "\uF133\u2583\u2713\uF135\uF136\u2518\uF137\u2592"
)

UC_CHARMAP = (
    "\uFFFE\uFFFE\uFFFE\uFFFE\uFFFE\uF100\uFFFE\uFFFE"
    "\uF118\uF119\uFFFE\uFFFE\uFFFE\u000D\u000E\uFFFE"
    "\uFFFE\uF11C\uF11A\uF120\u007F\uFFFE\uFFFE\uFFFE"
    "\uFFFE\uFFFE\uFFFE\uFFFE\uF101\uF11D\uF102\uF103"
    "\u0020\u0021\u0022\u0023\u0024\u0025\u0026\u0027"
    "\u0028\u0029\u002A\u002B\u002C\u002D\u002E\u002F"
    "\u0030\u0031\u0032\u0033\u0034\u0035\u0036\u0037"
    "\u0038\u0039\u003A\u003B\u003C\u003D\u003E\u003F"
    "\u0040\u0041\u0042\u0043\u0044\u0045\u0046\u0047"
    "\u0048\u0049\u004A\u004B\u004C\u004D\u004E\u004F"
    "\u0050\u0051\u0052\u0053\u0054\u0055\u0056\u0057"
    "\u0058\u0059\u005A\u005B\u00A3\u005D\u2191\u2190"
    "\u2501\u2660\u2502\u2501\uF122\uF123\uF124\uF126"
    "\uF128\u256E\u2570\u256F\uF12A\u2572\u2571\uF12B"
    "\uF12C\u25CF\uF125\u2665\uF127\u256D\u2573\u25CB"
    "\u2663\uF129\u2666\u253C\uF12E\u2502\u03C0\u25E5"
    "\uFFFE\uF104\uFFFE\uFFFE\uFFFE\uF110\uF112\uF114"
    "\uF116\uF111\uF113\uF115\uF117\u000A\u000F\uFFFE"
    "\uF105\uF11E\uF11B\u000C\uF121\uF106\uF107\uF108"
    "\uF109\uF10A\uF10B\uF10C\uF10D\uF11D\uF10E\uF10F"
    "\u00A0\u258C\u2584\u2594\u2581\u258F\u2592\u2595"
    "\uF12F\u25E4\uF130\u251C\uF134\u2514\u2510\u2582"
    "\u250C\u2534\u252C\u2524\u258E\u258D\uF131\uF132"
    "\uF133\u2583\uF12D\uF135\uF136\u2518\uF137\uF138"
    "\u2501\u2660\u2502\u2501\uF122\uF123\uF124\uF126"
    "\uF128\u256E\u2570\u256F\uF12A\u2572\u2571\uF12B"
    "\uF12C\u25CF\uF125\u2665\uF127\u256D\u2573\u25CB"
    "\u2663\uF129\u2666\u253C\uF12E\u2502\u03C0\u25E5"
    "\u00A0\u258C\u2584\u2594\u2581\u258F\u2592\u2595"
    "\uF12F\u25E4\uF130\u251C\uF134\u2514\u2510\u2582"
    "\u250C\u2534\u252C\u2524\u258E\u258D\uF131\uF132"
    "\uF133\u2583\uF12D\uF135\uF136\u2518\uF137\u03C0"
)

DECODING_TABLES = {
    LC_CODEC: LC_CHARMAP,
    UC_CODEC: UC_CHARMAP,
}

ENCODING_TABLES = {
    key: codecs.charmap_build(DECODING_TABLES[key]) for key in [LC_CODEC, UC_CODEC]
}


def encode_fn(table):
    """
    Get an encoding function that operates on the provided table.
    :param table: The encoding table.
    :return: An encoding function.
    """

    def encode(text: str, errors: str = "strict") -> typing.Tuple[bytes, int]:
        """
        Encode the provided text to binary, using the encoding specified by the outer
        function.
        :param text: Text to encode.
        :param errors: Error handling mode.
        :return: The size and encoded data as a tuple.
        """
        return codecs.charmap_encode(text, errors, table)

    return encode


def decode_fn(table):
    """
    Get a decoding function that operates on the provided table.
    :param table: The decoding table.
    :return: A decoding function.
    """

    def decode(binary: bytes, errors: str = "strict") -> typing.Tuple[str, int]:
        """
        Decode the provided binary to text, using the encoding specified by the outer
        function.
        :param binary: Data to decode.
        :param errors: Error handling mode.
        :return: The size and decoded data as a tuple.
        """
        return codecs.charmap_decode(binary, errors, table)

    return decode


def codec_info(encoding: str) -> codecs.CodecInfo:
    """
    Generate a CodecInfo object for the specified encoding.
    :param encoding: The encoding name.
    :return: A CodecInfo object.
    :raises: KeyError
    """
    e_table = ENCODING_TABLES[encoding]
    d_table = DECODING_TABLES[encoding]
    return codecs.CodecInfo(encode_fn(e_table), decode_fn(d_table), name=encoding)


CODEC_INFOS = {key: codec_info(key) for key in [LC_CODEC, UC_CODEC]}
