import unittest
import struct
from uavision_gimbal_decoder.klv_decoder import klv_types_data
import uavision_gimbal_decoder.decoders as klv_decoder


class MyTestCase(unittest.TestCase):
    def test_decode_output_range(self):
        for tag, packet_type_data in klv_types_data.items():
            # test value range
            if packet_type_data.min_val is not None and \
               packet_type_data.max_val is not None:
                # when input range goes from 0 to 2^(number of bits - 1)
                if not packet_type_data.negative_input_value:
                    min_input_val = bytes.fromhex('0' * packet_type_data.exact_input_size * 2)
                    max_input_val = bytes.fromhex('F' * packet_type_data.exact_input_size * 2)
                else:
                    raise NotImplementedError()
                    bis = packet_type_data.exact_input_size * 8 - 1
                    min_input_val = -(2 ** bits - 1)
                    min_input_bytes = ...
                    max_input_val = bytes.fromhex('0' * packet_type_data.exact_input_size)

                computed_min_output_val = packet_type_data.decode_func(min_input_val)
                self.assertEqual(computed_min_output_val, packet_type_data.min_val,
                                 f'min value for {packet_type_data.description} \
                                 (tag {packet_type_data.tag}) is {packet_type_data.min_val},\
                                 got {computed_min_output_val}')

                computed_max_output_val = packet_type_data.decode_func(max_input_val)
                self.assertEqual(computed_max_output_val, packet_type_data.max_val,
                                 f'max value for {packet_type_data.description} (tag {packet_type_data.tag}) is {packet_type_data.max_val}, got {computed_max_output_val}')






    def test_decode_input_size(self):
        funcs = [(klv_decoder.decodeTimeStamp, 8, 'Tag 2 - UNIX timestamp'),
                 (klv_decoder.decodePlatformHeadingAngle, 2, 'Tag 5 - Platform Heading Angle'),
                 (klv_decoder.decodePlatformPitchAngle, 2, 'Tag 6 - Platform Pitch Angle'),
                 (klv_decoder.decodePlatformRollAngle, 2, 'Tag 7 - Platform Roll Angle'),
                 (klv_decoder.decodeLatitude, 4, 'Tag 13 - Sensor Latitude'),
                 (klv_decoder.decodeLongitude, 4, 'Tag 14 - Sensor Longitude'),
                 (klv_decoder.decodeAltitude, 2, 'Tag 15 - Sensor Altitude'),
                 ]
        for decode_func, correct_size, msg in funcs:
            # too small
            self.assertRaises(Exception, decode_func, b'd' * (correct_size - 1))
            self.assertRaises(Exception, decode_func, b'd' * (correct_size + 1))



    def test_decode_altitude_input_size(self):
        self.assertRaises(Exception, klv_decoder.decodeAltitude, b'ddd')
        self.assertRaises(Exception, klv_decoder.decodeAltitude, b'd')

    def test_decode_altitude(self):
        packet_payload = bytes.fromhex('c221')
        uint16 = struct.unpack('>H', packet_payload)[0]
        true_value = (19900/0xFFFF) * uint16 - 900

        self.assertEqual(klv_decoder.decodeAltitude(bytes.fromhex('0000')), -900, 'min altitude value must be -900 meters')
        self.assertEqual(klv_decoder.decodeAltitude(bytes.fromhex('FFFF')), 19000, 'max altitude value must be 19000 meters')
        self.assertEqual(klv_decoder.decodeAltitude(packet_payload), true_value)


if __name__ == '__main__':
    unittest.main()
