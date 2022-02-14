from .utils import *
import struct


def encode_length(length: int) -> bytes:
    # translate to bytes, padding zeros
    length_hex = to_hex_padded(length)

    is_longform = length >= 128
    if not is_longform:
        return bytes.fromhex(length_hex)
    else:
        first_byte = 0b10000000 | len(length_hex)
        return bytes.fromhex(to_hex_padded(first_byte) + length_hex)


def mk_crc_field(values: bytes) -> bytes:
    tag_byte = struct.pack(">B", 1)
    length_byte = struct.pack(">B", 2)
    computed_crc = computeCrc(values + tag_byte + length_byte)
    return tag_byte + length_byte + struct.pack(">H", computed_crc)


def encode_field(tag: int, payload: bytes) -> bytes:
    return struct.pack('>B', tag) + encode_length(len(payload)) + payload
