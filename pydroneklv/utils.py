def to_hex_padded(num: int) -> str:
    """integer to bytes, using minimum number of bytes necessary"""
    num_hex = hex(num)[2:]  # drop the '0x' part
    if len(num_hex) % 2 != 0:  # pad a zero if necessary
        num_hex = '0' + num_hex
    assert (len(num_hex) % 2) == 0
    return num_hex


def computeCrc(buf: bytes) -> int:
    crc = 0
    for i, b in enumerate(buf):
        crc += b << (8 * ((i + 1) % 2))
    return crc & 0xffff