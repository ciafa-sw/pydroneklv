import datetime
import struct

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


def decodeTimeStamp(buf):
    """
    // unix timestamp
                    var buffer = [];
                    for (var i = 0; i < length; i++) {
                        buffer.push((this.bits.read(8)).toString(16)); // Read one byte at a time
                    }
                    var unix_timestamp = bigInt(buffer.join(''), 16).toString();
                    return new Date(unix_timestamp / 1000); // Convert from microseconds to milliseconds, and return
    """
    uInt64 = struct.unpack(">Q", buf)[0]
    dt = datetime.datetime.fromtimestamp(uInt64 / 1000000)  # convert µs to seconds
    return dt


def decodePlatformHeadingAngle(buf):
    int16 = struct.unpack(">h", buf)[0]
    return (360 / 65535) * int16


def decodePlatformPitchAngle(buf):
    int16 = struct.unpack(">h", buf)[0]
    return (40 / 65534) * int16


def decodePlatformRollAngle(buf):
    int16 = struct.unpack(">h", buf)[0]
    return (100 / 65534) * int16


def decodeString(buf):
    return buf.decode("ascii")


def decodeLatitude(buf):
    int32 = struct.unpack(">i", buf)[0]
    return 180 / 0xFFFFFFFE * int32


def decodeLongitude(buf):
    int32 = struct.unpack(">i", buf)[0]
    return 360 / 0xFFFFFFFE * int32


def decodeAltitude(buf: bytes) -> float:
    if len(buf) != 2:
        raise Exception('altitude is 2 bytes')
    uInt16 = struct.unpack(">H", buf)[0]
    return 19900 / 0xFFFF * uInt16 - 900


def decodeSensorFOV(buf):
    # same convertion calculation for horizontal and vertical
    uInt16 = struct.unpack(">H", buf)[0]
    return 180 / 0xFFFF * uInt16


def decodeSensorRelAngle(buf):
    # same convertion calculation for azimuth, elevation and roll
    uInt32 = struct.unpack(">I", buf)[0]
    return 360 / 0xFFFFFFFF * uInt32


def decodeSlantRange(buf):
    uInt32 = struct.unpack(">I", buf)[0]
    return 5000000 / 0xFFFFFFFF * uInt32


def decodeTargetWidth(buf):
    uInt16 = struct.unpack(">H", buf)[0]
    return 10000 / 0xFFFF * uInt16


def decodeUasLdsVersion(buf):
    return struct.unpack(">B", buf)[0]


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


def checksum(packet):
    i = 0
    cs = 0
    while i < len(packet) - 2:
        cs += (packet[i] << (8 * ((i + 1) % 2)))
        cs = cs % (2 ** 16)
        i += 1

    return cs == (packet[-2] << 8 + packet[-1])


def computeCrc(buf):
    crc = 0
    for i, b in enumerate(buf):
        crc += b << (8 * ((i + 1) % 2))
    return crc & 0xffff


def verifyCrc_old(p):
    packetCrc = (p[-2] << 8) + p[-1]
    computedCrc = computeCrc(p[:-2])
    return packetCrc == computedCrc


def verifyCrc(p, startIndex, size):
    packetCrc = (p[size - 2] << 8) + p[size - 1]
    computedCrc = computeCrc(p[startIndex:size - 2])
    return packetCrc == computedCrc





def decodePacket(buf, startIndex=0):
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