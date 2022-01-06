import unittest
import struct
from uavision_gimbal_decoder.klv_decoder import klv_types_data
import uavision_gimbal_decoder.decoders as klv_decoder

struct_letters =\
    {'uint8': 'B',
     'int8': 'b',
     'uint16': 'H',
     'int16': 'h',
     'uint32': 'I',
     'int32': 'i',
     'uint64': 'Q',
     'int64': 'q',
     }

class MyTestCase(unittest.TestCase):
    def test_decode_output_min_max(self):
        for tag, packet_type_data in klv_types_data.items():
            # test value range
            if packet_type_data.min_input_val is not None and \
               packet_type_data.max_input_val is not None and \
               packet_type_data.min_output_val is not None and \
               packet_type_data.max_output_val is not None and \
               packet_type_data.input_type in struct_letters:
                # construct bytes array from min and max input values according to declared
                # input type
                struct_format_str = '>' + struct_letters[packet_type_data.input_type]

                print(packet_type_data.description, struct_format_str)

                min_input_payload = struct.pack(struct_format_str, packet_type_data.min_input_val)
                max_input_payload = struct.pack(struct_format_str, packet_type_data.max_input_val)

                computed_min_output_val = packet_type_data.decode_func(min_input_payload)
                self.assertEqual(computed_min_output_val, packet_type_data.min_output_val,
                                 f'min value for {packet_type_data.description} \
                                 (tag {packet_type_data.tag}) is {packet_type_data.min_output_val},\
                                 got {computed_min_output_val} - {packet_type_data.min_input_val}')

                computed_max_output_val = packet_type_data.decode_func(max_input_payload)
                self.assertEqual(computed_max_output_val, packet_type_data.max_output_val,
                                 f'max value for {packet_type_data.description} (tag {packet_type_data.tag}) is {packet_type_data.max_output_val}, got {computed_max_output_val}')

    def test_decode_input_size(self):
        for tag, packet_type_data in klv_types_data.items():
            if packet_type_data.exact_input_size is not None:
                self.assertRaises(Exception, packet_type_data.decode_func, b'd' * (packet_type_data.exact_input_size - 1))
                self.assertRaises(Exception, packet_type_data.decode_func, b'd' * (packet_type_data.exact_input_size + 1))

    def test_decode_altitude(self):
        packet_payload = bytes.fromhex('c221')
        uint16 = struct.unpack('>H', packet_payload)[0]
        true_value = (19900/0xFFFF) * uint16 - 900

        self.assertEqual(klv_decoder.decodeAltitude(packet_payload), true_value)


if __name__ == '__main__':
    unittest.main()
