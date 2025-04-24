from app.se_string import SliceCursor


def read_packed_u32(cursor_bytes_: bytes, kind: int) -> int:
    cursor = SliceCursor(cursor_bytes_)
    f"{kind + 1:b}"
    f"{0xF0:b}"
    f"{0xFE:b}"
    flags = (kind + 1) & 0b1111
    bytes_ = [0] * 4
    for i in reversed(range(4)):
        if flags & (1 << i):
            bytes_[i] = cursor.next() or 0
    return int.from_bytes(bytes_, "little")


def write_packed_u32(value: int) -> bytes:
    bytes_ = value.to_bytes(4, byteorder="big")
    bits_str = ""
    i = 3
    for byte in bytes_:
        if byte:
            bits_str += "1"
        else:
            bits_str += "0"
        i -= 1
    flags = int(bits_str, 2)
    kind = 0xF0 + flags - 1
    packed_u32 = [kind]
    for i, bit in enumerate(bits_str):
        if int(bit):
            packed_u32 += [bytes_[i]]
    return bytes(packed_u32)
