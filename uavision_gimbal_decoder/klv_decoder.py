
from typing import Optional, Callable, Dict
from .decoders import *
# check is there are enough bytes for a minimum packet =
# universal key   16 bytes
# size bytes       2 bytes
# timestamp       10 bytes
# CRC              4 bytes
# ---------------------
# total       =
MINIMUM_PACKET_SIZE = 16 + 2 + 10 + 4

# Universal key - 16 bytes
ukey_hex = "060E2B34020B01010E01030101000000"
bukey = bytearray.fromhex(ukey_hex)

class PacketTypeData:
    def __init__(self,
                 tag: int,
                 description: str,
                 decode_func: Optional[Callable] = None,
                 input_type: str = '',
                 min_input_val: Optional[float] = None,
                 max_input_val: Optional[float] = None,
                 min_output_val: Optional[float] = None,
                 max_output_val: Optional[float] = None,
                 negative_input_value: Optional[bool] = False,
                 exact_input_size: Optional[int] = None,
                 min_input_size: Optional[int] = None,
                 max_input_size: Optional[int] = None):
        # min_val, max_val, negative_input_value, exact_input_size have to be offered together
        self.tag = tag
        self.description = description
        self.decode_func = decode_func
        self.input_type = input_type
        self.min_input_val = min_input_val
        self.max_input_val = max_input_val
        self.min_output_val = min_output_val
        self.max_output_val = max_output_val
        self.negative_input_value = negative_input_value
        self.exact_input_size = exact_input_size
        self.min_input_size = min_input_size
        self.max_input_size = max_input_size


klv_types_data: Dict[int, PacketTypeData] = {}

def add_klv_type(tag: int,
                 description: str,
                 decode_func: Optional[Callable] = None,
                 input_type: str = '',
                 min_input_val: Optional[float] = None,
                 max_input_val: Optional[float] = None,
                 min_output_val: Optional[float] = None,
                 max_output_val: Optional[float] = None,
                 negative_input_value: Optional[bool] = None,
                 exact_input_size: Optional[int] = None,
                 min_input_size: Optional[int] = None,
                 max_input_size: Optional[int] = None):
    packet_data = PacketTypeData(tag=tag,
                                 description=description,
                                 decode_func=decode_func,
                                 input_type=input_type,
                                 min_input_val=min_input_val,
                                 max_input_val=max_input_val,
                                 min_output_val=min_output_val,
                                 max_output_val=max_output_val,
                                 negative_input_value=negative_input_value,
                                 exact_input_size=exact_input_size,
                                 min_input_size=min_input_size,
                                 max_input_size=max_input_size
                                 )
    klv_types_data[tag] = packet_data
    return packet_data


add_klv_type(1, "Checksum")
add_klv_type(2, "UNIX Time Stamp", decodeTimeStamp, exact_input_size=8)
add_klv_type(3, "Mission ID", max_input_size=127)
add_klv_type(4, "Platform Tail Number", max_input_size=127)
add_klv_type(5, "Platform Heading Angle", decodePlatformHeadingAngle,
             input_type='uint16',
             min_input_val=0,
             max_input_val=2**16-1,
             min_output_val=0.0,
             max_output_val=360.0,
             exact_input_size=2)
add_klv_type(6, "Platform Pitch Angle", decodePlatformPitchAngle,
             input_type='int16',
             min_input_val=-(2 ** 15 - 1),
             max_input_val=2 ** 15 - 1,
             min_output_val=-20.0,
             max_output_val=+20.0,
             exact_input_size=2)
add_klv_type(7, "Platform Roll Angle", decodePlatformRollAngle,
             input_type='int16',
             min_input_val=-(2 ** 15 - 1),
             max_input_val=2 ** 15 - 1,
             min_output_val=-50.0,
             max_output_val=+50.0,
             exact_input_size=2)
add_klv_type(13, "Sensor latitude", decodeLatitude,
             input_type='int32',
             min_input_val=-(2 ** 31 - 1),
             max_input_val=2 ** 31 - 1,
             min_output_val=-90.0,
             max_output_val=+90.0,
             exact_input_size=4)
add_klv_type(14, "Sensor longitude", decodeLongitude,
             input_type = 'int32',
             min_input_val = -(2 ** 31 - 1),
             max_input_val = 2 ** 31 - 1,
             min_output_val = -180.0,
             max_output_val = +180.0,
             exact_input_size = 4)
add_klv_type(15, "Sensor true altitude", decodeAltitude,
             input_type='uint16',
             min_input_val = 0,
             max_input_val = 2 ** 16 - 1,
             min_output_val = -900.0,
             max_output_val = +19000.0,
             exact_input_size = 2)


klv_types = {1: ("Checksum", None),
             2: ("UNIX Time Stamp", decodeTimeStamp),
             3: ("Mission ID", None),
             4: ("Platform Tail Number", None),
             5: ("Platform heading angle", decodePlatformHeadingAngle),
             6: ("Platform pitch angle", decodePlatformPitchAngle),
             7: ("Platform roll angle", decodePlatformRollAngle),

             10: ("Platform Designation", decodeString),
             11: ("Image Source Sensor", decodeString),
             12: ("Image Coordinate System", decodeString),
             13: ("Sensor latitude", decodeLatitude),
             14: ("Sensor longitude", decodeLongitude),
             15: ("Sensor true altitude", decodeAltitude),
             16: ("Sensor horizontal FOV", decodeSensorFOV),
             17: ("Sensor vertical FOV", decodeSensorFOV),
             18: ("Sensor Rel. Azimuth angle", decodeSensorRelAngle),
             19: ("Sensor Rel. Elevation angle", decodeSensorRelAngle),
             20: ("Sensor Rel. Roll angle", decodeSensorRelAngle),
             21: ("Slant range", decodeSlantRange),
             22: ("Target width", decodeTargetWidth),
             23: ("Frame center latitude", decodeLatitude),
             24: ("Frame center longitude", decodeLongitude),
             25: ("Frame center elevation", decodeAltitude),
             26: ("Offset Corner Latitude Point 1", None),
             27: ("Offset Corner Longitude Point 1", None),
             28: ("Offset Corner Latitude Point 2", None),
             29: ("Offset Corner Longitude Point 2", None),
             30: ("Offset Corner Latitude Point 3", None),
             31: ("Offset Corner Longitude Point 3", None),
             32: ("Offset Corner Latitude Point 4", None),
             33: ("Offset Corner Longitude Point 4", None),
             40: ("Target Location Latitude", decodeLatitude),
             41: ("Target Location Longitude", decodeLongitude),
             42: ("Target Location Elevation", decodeAltitude),
             43: ("Target Track Gate Width", None),
             44: ("Target Track Gate Height", None),
             48: ("Security Local Metadata Set", None),
             65: ("UAS LDS version", decodeUasLdsVersion),
             74: ("VMTI Data SetConversion", None),
             94: ("MIIS Core Identifier", None),
             }




def decodePacket(buf: bytes, startIndex: int = 0) -> dict:
    # check minimum size packet
    nBytesFromStart = len(buf) - startIndex
    if nBytesFromStart < MINIMUM_PACKET_SIZE:
        raise Exception("not enough bytes {} for a packet {} = ".format(MINIMUM_PACKET_SIZE, nBytesFromStart))

    i = startIndex

    # verify universal key
    if not buf[i:i + 16] == bukey:
        raise Exception(
            "universal key not ok starting on index {} = ".format(startIndex, buf[startIndex:starIndex + 16]))

    i += 16  # skip universal key

    # read size of packet
    longform = buf[i] >= 128
    klvSize = 0
    if longform:
        sizeBytes = buf[i] - 128
        i += 1  # i=17
        while i < 17 + sizeBytes:
            klvSize = klvSize << 8
            klvSize += buf[i]
            i += 1
    else:
        klvSize = buf[i] - 128  # i=16
        i += 1

    # print("longform:", longform)
    # print(klvSize, len(p[i:]))

    # check if there are enough bytes
    parsedPacketSize = i + klvSize

    if nBytesFromStart < parsedPacketSize:
        raise Exception(
            "size error: remaining bytes from start index({})={}, parsed size={}".format(startIndex, nBytesFromStart,
                                                                                         parsedPacketSize))

    if not verifyCrc(buf, startIndex, parsedPacketSize):
        raise Exception("CRC error")

    packet = {}
    j = 0
    while j < klvSize:
        tag = buf[i + j]
        tag_len = buf[i + j + 1]
        tag_payload = buf[i + j + 2:i + j + 2 + tag_len]

        tag_stuff = klv_types.get(tag, ("unknown", None))
        tag_description, decodingFunc = tag_stuff

        if decodingFunc:
            decodedValue = decodingFunc(tag_payload)
        else:
            decodedValue = tag_payload
        packet[tag] = (tag_description, tag_len, tag_payload, decodedValue)
        j += 2 + tag_len
    return packet