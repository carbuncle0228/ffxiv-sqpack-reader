import os
import zlib


def compute_crc32(value: str):
    if value is None:
        raise ValueError("value cannot be None")
    byte_data = value.encode("ascii")

    return _compute_crc32_jamcrc(byte_data)


def get_file(sqpack, file_path):
    _folder, file_name = os.path.split(str.lower(file_path))
    return sqpack.file_keymap.get(compute_crc32(file_name))


def _compute_crc32_jamcrc(byte_data):
    crc32_jamcrc = 0xFFFFFFFF - zlib.crc32(byte_data)

    return crc32_jamcrc


def calculate_path_hash(path):
    # Convert the path to lowercase
    path = path.lower()

    # Find the last instance of '/' and split the string
    directory, filename = os.path.split(path)

    # Calculate CRC32 of both path segments
    directory_hash = compute_crc32(directory)
    filename_hash = compute_crc32(filename)

    # Join both CRC32s into a u64
    """
    struct IndexHashTableEntry
    {
        uint64_t hash;
        uint32_t unknown : 1;
        uint32_t dataFileId : 3;
        uint32_t offset : 28;
        uint32_t _padding;
    };
    combined_hash == hash
    """
    combined_hash = (directory_hash << 32) | filename_hash

    return combined_hash
