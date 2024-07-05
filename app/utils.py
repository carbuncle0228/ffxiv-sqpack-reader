import zlib


def compute_crc32(value: str):
    if value is None:
        raise ValueError("value cannot be None")
    byte_data = value.encode("ascii")

    return _compute_crc32_jamcrc(byte_data)


def _compute_crc32_jamcrc(byte_data):
    crc32_jamcrc = 0xFFFFFFFF - zlib.crc32(byte_data)

    return crc32_jamcrc
