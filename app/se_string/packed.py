def get_packed_u32_bytes(value: int) -> bytes:
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


def get_length_bytes_str(bytes_: bytes) -> str:
    len_bytes = len(bytes_) + 1
    if len_bytes <= 0xCF:
        return f"{len_bytes:02X}"
    else:
        return "".join(f"{b:02X}" for b in get_packed_u32_bytes(len_bytes))


def get_length_bytes(bytes_: bytes) -> bytes:
    len_bytes = len(bytes_) + 1
    if len_bytes <= 0xCF:
        return [len_bytes]
    else:
        return get_packed_u32_bytes(len_bytes)
