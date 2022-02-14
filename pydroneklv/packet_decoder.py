from .decoder_map import klv_types_data, klv_types
from .decoder_map import UNIVERSAL_KEY as BYTES_UKEY
from .decoders import verify_crc, decode_length
from .errors import *

from typing import Optional, Tuple
from collections import namedtuple

KlvField = namedtuple('KlvField', "name len bytes value")


# check is there are enough bytes for a minimum packet =
# universal key   16 bytes
# size bytes       1 bytes
# timestamp       10 bytes
# CRC              4 bytes
# ---------------------
# total       =
MIN_LEN_FIELD_SIZE = 1
TIMESTAMP_SIZE = 10
CRC_SIZE = 4
MINIMUM_PACKET_SIZE = len(BYTES_UKEY) + MIN_LEN_FIELD_SIZE + TIMESTAMP_SIZE + CRC_SIZE


def is_packet_start(buf: bytes, idx: int, packet_header: bytes = BYTES_UKEY) -> bool:
    return buf[idx:idx+len(packet_header)] == packet_header


def has_min_size(buf: bytes, idx: int = 0) -> bool:
    n_bytes_from_start = len(buf) - idx
    return n_bytes_from_start >= MINIMUM_PACKET_SIZE


def search_packet_start(buf: bytes, idx: int) -> Optional[int]:
    """receives a buffer and a start index
    returns the index at which the packet header starts or None if it's not found
    """
    while has_min_size(buf, idx):
        if is_packet_start(buf, idx):
            idx += len(BYTES_UKEY)  # skip universal key
            return idx
        idx += 1
    return None


def decode_field(buf: bytes, idx: int = 0) -> Tuple[int, int, bytes]:
    """
    receives a bytes buffer and the index to start decoding
    assumes first bytes is tag number
    following length encoded bytes
    following payload bytes

    returns a tuple of:
    - number of bytes in the tag, including tag key, bytes encoding length and value bytes
    - tag key
    - value bytes
    """
    tag = buf[idx]
    n_tag_len_bytes, tag_len = decode_length(buf, idx + 1)

    tag_payload_start = idx + 1 + n_tag_len_bytes  # +1 for tag byte
    tag_payload = buf[tag_payload_start:tag_payload_start + tag_len]

    return 1+n_tag_len_bytes+tag_len, tag, tag_payload


def decode_packet(buf: bytes, start_index: int = 0) -> dict:
    buf = buf[start_index:]
    if not has_min_size(buf):
        raise ByteArrayTooSmall()

    idx = buf.find(BYTES_UKEY)
    if idx == -1:
        raise UniversalKeyNotFound()

    idx += len(BYTES_UKEY)  # move index to start of length field
    n_length_bytes, payload_length = decode_length(buf, idx)
    idx += n_length_bytes  # move index to start of payload

    # check if there are enough bytes in buffer
    remaining_bytes = len(buf) - idx
    if remaining_bytes < payload_length:
        raise ByteArrayTooSmall(
            f"size of payload bytes={remaining_bytes} =/= parsed size={payload_length}")

    total_size = len(BYTES_UKEY) + n_length_bytes + payload_length
    if not verify_crc(buf, start_index, total_size):
        raise CRCError()

    packet = {}
    payload_start = idx
    tag_start = 0  # tag start index, relative to the payload start index
    while tag_start < payload_length:
        n_tag_bytes, tag, tag_payload = decode_field(buf, payload_start+tag_start)

        if tag in klv_types_data:  # the new list for decoder maps
            type_data = klv_types_data[tag]
            tag_description = type_data.description
            decode_func = type_data.decode_func
        elif tag in klv_types:  # old list of decoder map
            tag_description, decode_func = klv_types[tag]
        else:  # non existent decoder
            tag_description, decode_func = ("unknown", None)

        if decode_func:
            decoded_value = decode_func(tag_payload)
        else:
            decoded_value = tag_payload

        packet[tag] = KlvField(name=tag_description,
                               len=len(tag_payload),
                               bytes=tag_payload,
                               value=decoded_value)

        tag_start += n_tag_bytes
    return packet
