import unittest

from pydroneklv.packet_decoder import decode_packet
import pydroneklv.decoder_map as decoder_map
import pydroneklv.encoders as encoders

from typing import List, TypedDict, Any
from collections import namedtuple

TestField = namedtuple('TestField', 'tag len bytes value')


class TestPacketPayload(TypedDict):
    fields: List[TestField]
    bytes: bytes


def mk_field(tag: int, tag_type: decoder_map.PacketTypeData) -> TestField:
    value_bytes = bytes.fromhex(tag_type.example_input_output_values[0])
    f = TestField(tag=tag,
                  len=len(value_bytes),
                  bytes=encoders.encode_field(tag, value_bytes),
                  value=tag_type.example_input_output_values[1])
    return f


def mk_packet(payload: TestPacketPayload, ukey: bytes = decoder_map.UNIVERSAL_KEY) \
        -> bytes:
    # build length field for entire payload
    packet_len = encoders.encode_length(len(payload['bytes']) + 4)   # checksum field is 4 bytes

    packet_bytes = ukey + packet_len + payload['bytes']

    packet_bytes += encoders.mk_crc_field(packet_bytes)
    return packet_bytes


def mk_payload() -> TestPacketPayload:
    payload = []
    for tag, tag_type in decoder_map.klv_types_data.items():
        if tag_type.example_input_output_values is None:
            continue
        payload.append(mk_field(tag, tag_type))
    payload_bytes = b''.join([f.bytes for f in payload])
    return {'fields': payload, 'bytes': payload_bytes}


class TestPacket:
    def __init__(self):
        payload: TestPacketPayload = mk_payload()
        self.payload_fields = payload['fields']
        self.payload_bytes = payload['bytes']
        self.pkt_bytes: bytes = mk_packet(payload)


def compare_klv_values(tag: int, v1: Any, v2: Any) -> bool:
    """if there is a resolution to a specific KLV field, use that as margin of error
    otherwise, check equality"""
    if tag in decoder_map.klv_types_data:
        klv_field_meta = decoder_map.klv_types_data[tag]
        if klv_field_meta.resolution is not None:
            return (v2 - v1) <= klv_field_meta.resolution
    return v1 == v2


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.pkt: TestPacket = TestPacket()
        self.decoded = decode_packet(self.pkt.pkt_bytes)
        self.decoded_keys = list(self.decoded.keys())  # keys by order of insertion (dict is OrderedDict by default)

    def test_fields_order(self):
        self.assertEqual(2, self.decoded_keys[0], 'timestamp mandatory and must be first field')
        self.assertEqual(1, self.decoded_keys[-1], 'checksum mandatory and must be last field')

        payload_tags = [f.tag for f in self.pkt.payload_fields]
        # test payload doesn't have checksum, so we remove it from the decoded fields too
        # we already tested that it exists in the correct order (last)
        self.assertEqual(payload_tags, self.decoded_keys[:-1])

    def test_fields_values(self):
        for f in self.pkt.payload_fields:
            with self.subTest(f"testing value of {f} in decoded packet", f=f):
                decoded_val = self.decoded[f.tag].value
                self.assertTrue(compare_klv_values(f.tag, f.value, decoded_val),
                                f'tag {f.tag} {f.value} =/= {decoded_val}')
