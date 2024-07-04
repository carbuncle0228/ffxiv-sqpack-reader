# Define ctypes structures for the headers
from ctypes import LittleEndianStructure, c_char, c_uint8, c_uint32, c_uint64, c_int16


class SqPackHeader(LittleEndianStructure):
    _fields_ = [
        ("magic", c_char * 8),
        ("platform_id", c_uint8),
        ("padding0", c_uint8 * 3),
        ("size", c_uint32),
        ("version", c_uint32),
        ("type", c_uint32),
        ("unknown", c_uint8 * 936),
        ("sha1", c_uint8 * 20),
        ("padding1", c_uint8 * 44),
    ]

    @property
    def magic(self):
        return self.magic

    @property
    def platform_id(self):
        return self.platform_id

    @property
    def size(self):
        return self.size

    @property
    def version(self):
        return self.version

    @property
    def type(self):
        return self.type

    @property
    def sha1(self):
        return self.sha1


class SqPackIndexHeader(LittleEndianStructure):
    _fields_ = [
        ("size", c_uint32),
        ("type", c_uint32),
        ("index_data_offset", c_uint32),
        ("index_data_size", c_uint32),
        ("sha1", c_uint8 * 20),
        ("padding", c_uint8 * 988),
    ]

    @property
    def size(self):
        return self.size

    @property
    def type(self):
        return self.type

    @property
    def index_data_offset(self):
        return self.index_data_offset

    @property
    def index_data_size(self):
        return self.index_data_size

    @property
    def sha1(self):
        return self.sha1


class IndexHashTableEntry(LittleEndianStructure):
    _fields_ = [("hash", c_uint64), ("data", c_uint32), ("padding", c_uint32)]

    @property
    def filename_crc32(self):
        return self.hash & 0xFFFFFFFF

    @property
    def folder_crc32(self):
        return self.hash >> 32

    @property
    def unknown(self):
        return self.data & 0x1

    @property
    def data_file_id(self):
        return (self.data & 0b1110) >> 1

    @property
    def offset(self):
        return (self.data & ~0xF) * 0x08


class Index2HashTableEntry(LittleEndianStructure):
    _fields_ = [("hash", c_uint32), ("data", c_uint32)]

    @property
    def filename_crc32(self):
        return self.hash

    @property
    def data_file_id(self):
        return (self.data & 0b1110) >> 1

    @property
    def offset(self):
        return (self.data & ~0xF) * 0x08


class SqPackDataHeader(LittleEndianStructure):
    _fields_ = [
        ("size", c_uint32),
        ("null_1", c_uint32),
        ("unknown", c_uint32),
        (
            "data_size",
            c_uint32,
        ),  # From end of this header (usually 0x800) to EOF. Divided by 0x08.
        ("spanned_dat", c_uint32),  #  0x01 = .dat0, 0x02 = .dat1 or .dat2, etc
        ("null_2", c_uint32),
        ("max_file_size", c_uint32),  #  2GB
        ("null_3", c_uint32),
        ("sha1_data", c_uint8 * 20),  #  From end of this header (usually 0x800) to EOF
        (
            "padding",
            c_uint8 * 908,
        ),  # (0x3c0 - 0x20 -20) = 908 bytes of padding till sha1 of header
        ("sha1_header", c_uint8 * 20),  #  Starts 64bytes before end of header
        ("final_padding", c_uint8 * 44),  # 44 bytes of final padding
    ]

    @property
    def size(self):
        return self.size

    @property
    def unknown(self):
        return self.unknown

    @property
    def data_size(self):
        return self.data_size

    @property
    def spanned_dat(self):
        return self.spanned_dat

    @property
    def max_file_size(self):
        return self.max_file_size

    @property
    def sha1_data(self):
        return self.sha1_data

    @property
    def sha1_header(self):
        return self.sha1_header


class DataEntryHeader(LittleEndianStructure):
    _fields_ = (
        ("size", c_uint32),
        (
            "content_type",
            c_uint32,
        ),  # 0x01: empty placeholder, 0x02: binary, 0x03: model, 0x04: texture
        ("decompressed_size", c_uint32),
        ("unknown_1", c_uint32),
        ("block_buffer_size", c_uint32),
        ("num_blocks", c_uint32),
    )

    size: int
    content_type: int
    decompressed_size: int
    unknown_1: int
    block_buffer_size: int
    num_blocks: int


class Type2BlockTable(LittleEndianStructure):
    _fields_ = (
        ("offset", c_uint32),
        ("block_size", c_int16),
        ("decompressed_data_size", c_int16),
    )

    offset: int
    block_size: int
    decompressed_data_size: int


class Type4BlockTable(LittleEndianStructure):
    _fields_ = (
        ("frame_offset", c_uint32),
        ("frame_size", c_uint32),
        ("unknown", c_uint32),
        ("frame_blocksize_offset", c_uint32),
        ("frame_blocksize_count", c_uint32),
        ("frame_blocksize_size", c_uint32),
    )
    frame_offset: int
    frame_size: int

    frame_blocksize_offset: int
    frame_blocksize_count: int
    frame_blocksize_size: int
