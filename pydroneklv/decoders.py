import datetime
import struct

from typing import Tuple

from .utils import *


def raiseLenError(payload, correct_length):
    if len(payload) != correct_length:
        raise Exception(f'size of payload should be {correct_length} bytes, but got {len(payload)}')


def decode_timestamp_seconds(buf: bytes) -> int:
    return struct.unpack(">Q", buf)[0]


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
    uint64 = decode_timestamp_seconds(buf)
    dt = datetime.datetime.fromtimestamp(uint64 / 1e6)  # convert µs to seconds (*1e-6)
    return dt


def decodePlatformHeadingAngle(buf: bytes) -> float:
    # tag 5, page 38
    raiseLenError(buf, 2)
    uint16 = struct.unpack(">H", buf)[0]
    return (360 / 65535) * uint16


def decodePlatformPitchAngle(buf):
    # tag 6, page 40
    raiseLenError(buf, 2)
    int16 = struct.unpack(">h", buf)[0]
    return (40 / 65534) * int16


def decodePlatformRollAngle(buf):
    # tag 7, page 42
    raiseLenError(buf, 2)
    int16 = struct.unpack(">h", buf)[0]
    return (100 / 65534) * int16


def decodeString(buf):
    return buf.decode("ascii")


def decodeLatitude(buf):
    # tag 13, defined in page 52
    raiseLenError(buf, 4)
    int32 = struct.unpack(">i", buf)[0]
    return 180 / 0xFFFFFFFE * int32


def decodeLongitude(buf: bytes) -> float:
    # tag 14, defined in page 53
    raiseLenError(buf, 4)
    int32 = struct.unpack(">i", buf)[0]
    return 360 / 0xFFFFFFFE * int32


def decodeAltitude(buf: bytes) -> float:
    # tag 15, defined in page 54, example provided there is wrong
    raiseLenError(buf, 2)
    uInt16 = struct.unpack(">H", buf)[0]
    return 19900 / 0xFFFF * uInt16 - 900


def decodeSensorFOV(buf):
    # same convertion calculation for horizontal and vertical
    uInt16 = struct.unpack(">H", buf)[0]
    return 180 / 0xFFFF * uInt16


def decodeSensorRelAngle(buf):
    # same convertion calculation for azimuth, elevation and roll
    raiseLenError(buf, 4)
    uInt32 = struct.unpack(">I", buf)[0]
    return 360 / 0xFFFFFFFF * uInt32


def decodeSensorRelElevationAngle(buf):
    # same convertion calculation for azimuth, elevation and roll
    raiseLenError(buf, 4)
    uInt32 = struct.unpack(">i", buf)[0]
    return 360 / 0xFFFFFFFE * uInt32


def decodeSlantRange(buf):
    uInt32 = struct.unpack(">I", buf)[0]
    return 5000000 / 0xFFFFFFFF * uInt32


def decodeTargetWidth(buf: bytes) -> object:
    uInt16 = struct.unpack(">H", buf)[0]
    return 10000 / 0xFFFF * uInt16


def decodeUasLdsVersion(buf):
    return struct.unpack(">B", buf)[0]


def checksum(packet):
    i = 0
    cs = 0
    while i < len(packet) - 2:
        cs += (packet[i] << (8 * ((i + 1) % 2)))
        cs = cs % (2 ** 16)
        i += 1

    return cs == (packet[-2] << 8 + packet[-1])


def verifyCrc_old(p):
    packetCrc = (p[-2] << 8) + p[-1]
    computedCrc = computeCrc(p[:-2])
    return packetCrc == computedCrc


def verify_crc(p: bytes, startIndex: int, size: int) -> bool:
    packetCrc = (p[size - 2] << 8) + p[size - 1]
    computedCrc = computeCrc(p[startIndex:size - 2])
    return packetCrc == computedCrc


def decode_passthrough(buf: bytes) -> bytes:
    return buf


def decode_length(buf: bytes, idx: int = 0) -> Tuple[int, int]:
    """decode the length of the payload of a given packet
    returns a tuple (number of bytes encoding length, number of bytes of payload)

    """
    is_longform = buf[idx] & 0b10000000  # first bit specifies if long form or not

    if not is_longform:
        klv_size = buf[idx] & 0b01111111  # 7 last bits specify the length of the payload
        return 1, klv_size
    else:
        n_size_bytes = buf[idx] & 0b01111111  # 7 last bits specify the number of bytes encoding length
        klv_size = 0
        i = 1
        # TODO check if there are enough bytes
        while i <= n_size_bytes:
            klv_size = klv_size << 8
            klv_size += buf[idx+i]
            i += 1
        return 1 + n_size_bytes, klv_size  # the "1+" is for the first byte specifying how many length bytes exist
