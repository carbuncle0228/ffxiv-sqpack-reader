import hashlib
import struct
import os
from collections import namedtuple

# Define the path to the file
file_path = os.path.expanduser("~/project/ffxiv/sqpack/0a0000.win32.index2")

# Define the format string for struct.unpack
# SqPackHeader:
sqpack_header_fmt = "8s B 3x I I I 936x 20s 44x"
# SqPackIndexHeader:
sqpack_index_header_fmt = "I I I I 20s 988x"


SqPackHeader = namedtuple("SqPackHeader", "magic platformId size version type sha1")
SqPackIndexHeader = namedtuple(
    "SqPackIndexHeader", "size type indexDataOffset indexDataSize sha1"
)


def read_headers(file_path):
    with open(file_path, "rb") as f:
        # Read the SqPackHeader data
        sqpack_header_data = f.read(struct.calcsize(sqpack_header_fmt))
        sqpack_header = SqPackHeader._make(
            struct.unpack(sqpack_header_fmt, sqpack_header_data)
        )

        # Read the SqPackIndexHeader data
        sqpack_index_header_data = f.read(struct.calcsize(sqpack_index_header_fmt))
        sqpack_index_header = SqPackIndexHeader._make(
            struct.unpack(sqpack_index_header_fmt, sqpack_index_header_data)
        )

        return sqpack_header, sqpack_index_header


# Read the headers
sqpack_header, sqpack_index_header = read_headers(file_path)

# Print the SqPackHeader
print("SqPackHeader:")
print("Magic:", sqpack_header.magic.decode("utf-8").strip("\x00"))
print("Platform ID:", sqpack_header.platformId)
print("Size:", sqpack_header.size)
print("Version:", sqpack_header.version)
print("Type:", sqpack_header.type)
print("SHA1:", sqpack_header.sha1.hex())


def calculate_sha1(file_path, start, length):
    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read(length)
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()


sha1_hash = calculate_sha1(file_path, 0, 0x3C0)
print("\nSHA-1 of bytes 0x000-0x3BF:", sha1_hash)
# Print the SqPackIndexHeader
print("\nSqPackIndexHeader:")
print("Size:", sqpack_index_header.size)
print("Type:", sqpack_index_header.type)
print("Index Data Offset:", sqpack_index_header.indexDataOffset)
print("Index Data Size:", sqpack_index_header.indexDataSize)
print("SHA1:", sqpack_index_header.sha1.hex())
sha1_hash = calculate_sha1(
    file_path,
    sqpack_index_header.indexDataOffset,
    sqpack_index_header.indexDataSize,
)
print("\nSHA-1 of Index:", sha1_hash)

# IndexHashTableEntry:
index_hash_table_entry_fmt = "I I"

IndexHashTableEntry = namedtuple(
    "IndexHashTableEntry", "filename_crc32 dataFileId offset"
)


def read_index_hash_table_entries(file_path, offset, size, sort=True):
    entries = []
    entry_size = struct.calcsize(index_hash_table_entry_fmt)
    count = size // entry_size
    with open(file_path, "rb") as f:
        f.seek(offset)
        for _ in range(count):
            entry_data = f.read(entry_size)
            filename_crc32, data = struct.unpack(index_hash_table_entry_fmt, entry_data)
            dataFileId = (data & 0b1110) >> 1
            offset = (data & ~0xF) * 0x08
            entry = IndexHashTableEntry(filename_crc32, dataFileId, offset)
            entries.append(entry)
    if sort:
        entries.sort(key=lambda x: x.offset)

    return entries


def print_index_hash_table_entries(entries):
    print("\nIndexHashTableEntries:")
    for entry in entries:
        print(
            f"Filename CRC32: {entry.filename_crc32}, DataFileId: {entry.dataFileId}, Offset: {entry.offset}"
        )


# Read and print the IndexHashTableEntries
index_hash_table_entries = read_index_hash_table_entries(
    file_path, sqpack_index_header.indexDataOffset, sqpack_index_header.indexDataSize
)
# print_index_hash_table_entries(index_hash_table_entries)
