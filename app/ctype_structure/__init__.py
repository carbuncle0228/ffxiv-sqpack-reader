# Define ctypes structures for the headers
from _ctypes import sizeof
from ctypes import LittleEndianStructure, c_char, c_uint8, c_uint32, c_int16


class SqPackHeader(LittleEndianStructure):
    _fields_ = [
        ("magic", c_char * 8),
        ("platform_id", c_uint8),
        ("padding0", c_uint8 * 3),
        ("header_length", c_uint32),
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
    def header_length(self):
        return self.header_length

    @property
    def version(self):
        return self.version

    @property
    def type(self):
        return self.type

    @property
    def sha1(self):
        return self.sha1


class SegmentHeader(LittleEndianStructure):
    _fields_ = [
        ("type", c_uint32),
        ("segment_offset", c_uint32),
        ("segment_size", c_uint32),
        ("sha1", c_uint8 * 20),
    ]

    type: int
    segment_offset: int
    segment_size: int
    sha1: bytes  # Hash of the segment... [Segment Offset] to [Segment Offset] + [Segment Size]

    @property
    def segment_count(self):
        return self.segment_size // 0x10  # 0x10 entry size


class IndexHeader(LittleEndianStructure):
    header_length: int
    file_segment_header: SegmentHeader
    unknown_segment_header: SegmentHeader
    unknown_segment_header2: SegmentHeader
    folder_segment_header: SegmentHeader
    # Segment 1 is usually files, Segment 2/3 is unknown, Segment 4 is folders.

    _fields_ = (
        ("header_length", c_uint32),
        ("file_segment_header", SegmentHeader),
        ("padding1", c_uint8 * 0x2C),
        ("unknown_segment_header", SegmentHeader),
        ("padding2", c_uint8 * 0x28),
        ("unknown_segment_header2", SegmentHeader),
        ("padding3", c_uint8 * 0x28),
        ("folder_segment_header", SegmentHeader),
        ("padding4", c_uint8 * 0x28),
    )


class IndexFileSegment(LittleEndianStructure):
    _fields_ = [
        ("filename_hash", c_uint32),
        ("folder_hash", c_uint32),
        ("data", c_uint32),
        ("padding", c_uint32),
    ]

    @property
    def filename_hash(self):
        return self.filename_hash

    @property
    def folder_hash(self):
        return self.folder_hash

    @property
    def unknown(self):
        return self.data & 0x1

    @property
    def data_file_id(self):
        return (self.data & 0b1110) >> 1

    @property
    def offset(self):
        return (self.data & ~0xF) * 0x08


class IndexFolderSegment(LittleEndianStructure):
    file_keymap: dict[str, IndexFileSegment]
    _fields_ = [
        ("folder_hash", c_uint32),
        ("files_offset", c_uint32),  # Offset to file list in segment 1.
        (
            "files_size",
            c_uint32,
        ),  # Total size of all file segments for this folder. To find # files, divide by 0x10 (16).
        ("padding", c_uint32),
    ]

    @property
    def folder_hash(self):
        return self.folder_hash

    @property
    def files_offset(self):
        return self.files_offset

    @property
    def files_size(self):
        return self.files_size

    @property
    def files_count(self):
        return self.files_size // 0x10  # 0x10 entry size


class Index2Segment(LittleEndianStructure):
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


class DataHeader(LittleEndianStructure):
    _fields_ = [
        ("header_length", c_uint32),
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
    def header_length(self):
        return self.header_length

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
        ("header_length", c_uint32),
        (
            "content_type",
            c_uint32,
        ),  # 0x01: empty placeholder, 0x02: binary, 0x03: model, 0x04: texture
        ("decompressed_size", c_uint32),
        ("unknown_1", c_uint32),
        ("block_buffer_size", c_uint32),
        ("num_blocks", c_uint32),
    )

    header_length: int
    content_type: int
    decompressed_size: int
    unknown_1: int
    block_buffer_size: int
    num_blocks: int

    @property
    def length(self):
        """
        Important to note that any fields prepended with "Block" will mean that the number is in blocks,
         or units of 128-bytes.
         e.g., BlockOffset means that the offset in bytes would be calculated by BlockOffset << 7 or BlockOffset * 128.
        """
        return self.block_buffer_size * 128


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


class BlockHeader(LittleEndianStructure):
    _fields_ = (
        ("header_size", c_uint32),
        ("null", c_uint32),
        (
            "compressed_length",
            c_uint32,
        ),  # If this is 32000, IT'S NOT COMPRESSED. Use decompressed length to read the data in and just append
        ("decompressed_length", c_uint32),  # Will be max 16kb.
    )
    header_size: int
    null: int

    compressed_length: int
    decompressed_length: int

    @property
    def is_compressed(self):
        return self.compressed_length < 32000

    @classmethod
    def sizeof(cls) -> int:
        return sizeof(cls)
