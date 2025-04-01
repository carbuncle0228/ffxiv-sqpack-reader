# Define ctypes structures for the headers
import io
import os
from _ctypes import Structure, sizeof
from ctypes import (
    BigEndianStructure,
    LittleEndianStructure,
    c_bool,
    c_char,
    c_float,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
)
from enum import Enum
from io import BytesIO


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


class ExcelVariant(Enum):
    Unknown = 0
    Default = 1
    SubRows = 2

    @staticmethod
    def from_value(value):
        return {
            0: ExcelVariant.Unknown,
            1: ExcelVariant.Default,
            2: ExcelVariant.SubRows,
        }.get(value, ExcelVariant.Unknown)


class ExhHeader(BigEndianStructure):
    """
    https://xiv.dev/game-data/file-formats/excel#excel-header-.exh

    """

    _fields_ = (
        (
            "magic",
            c_char * 4,
        ),  #  The magic is always EXHF. If it's not, the file is probably not the file you're trying to read.
        ("unknown", c_uint16),
        ("data_offset", c_uint16),
        ("column_count", c_uint16),
        ("page_count", c_uint16),
        ("language_count", c_uint16),
        ("unknown1", c_uint16),
        ("u2", c_uint8),
        ("variant", c_uint8),
        ("u3", c_uint16),
        ("row_count", c_uint32),
        ("u4", c_uint32 * 2),
    )

    @classmethod
    def copy(cls, bytes_io) -> "ExhHeader":
        return cls.from_buffer_copy(bytes_io.read(sizeof(cls)))

    @property
    def magic(self):
        return self.magic

    @property
    def data_offset(self):
        return self.data_offset

    @property
    def column_count(self):
        return self.column_count

    @property
    def page_count(self):
        return self.page_count

    @property
    def language_count(self):
        return self.language_count

    @property
    def variant(self):
        return self.variant

    @property
    def variant_name(self) -> ExcelVariant:
        return ExcelVariant.from_value(self.variant)

    @property
    def row_count(self):
        return self.row


class ExcelColumnDataType(Enum):
    String = 0x0
    Bool = 0x1
    Int8 = 0x2
    UInt8 = 0x3
    Int16 = 0x4
    UInt16 = 0x5
    Int32 = 0x6
    UInt32 = 0x7
    Float32 = 0x9
    Int64 = 0xA
    UInt64 = 0xB
    # // 0 is read like data & 1, 1 is like data & 2, 2 = data & 4, etc...
    PackedBool0 = 0x19
    PackedBool1 = 0x1A
    PackedBool2 = 0x1B
    PackedBool3 = 0x1C
    PackedBool4 = 0x1D
    PackedBool5 = 0x1E
    PackedBool6 = 0x1F
    PackedBool7 = 0x20


PackedBoolTypes = {}
for i in range(8):
    class_name = f"PackedBoolType{i}"
    class_dict = {
        "_fields_": [("_value", c_bool)],
        "value": property(lambda self, idx=i: bool(self._value & (1 << idx))),
    }
    PackedBoolTypes[i] = type(class_name, (Structure,), class_dict)

type_mapping = {
    ExcelColumnDataType.String: c_uint32,
    ExcelColumnDataType.Bool: PackedBoolTypes[0],
    ExcelColumnDataType.Int8: c_int8,
    ExcelColumnDataType.UInt8: c_uint8,
    ExcelColumnDataType.Int16: c_int16,
    ExcelColumnDataType.UInt16: c_uint16,
    ExcelColumnDataType.Int32: c_int32,
    ExcelColumnDataType.UInt32: c_uint32,
    ExcelColumnDataType.Float32: c_float,
    ExcelColumnDataType.Int64: c_int64,
    ExcelColumnDataType.UInt64: c_uint64,
    ExcelColumnDataType.PackedBool0: PackedBoolTypes[0],
    ExcelColumnDataType.PackedBool1: PackedBoolTypes[1],
    ExcelColumnDataType.PackedBool2: PackedBoolTypes[2],
    ExcelColumnDataType.PackedBool3: PackedBoolTypes[3],
    ExcelColumnDataType.PackedBool4: PackedBoolTypes[4],
    ExcelColumnDataType.PackedBool5: PackedBoolTypes[5],
    ExcelColumnDataType.PackedBool6: PackedBoolTypes[6],
    ExcelColumnDataType.PackedBool7: PackedBoolTypes[7],
}


def create_dynamic_structure(type_list):
    field_defs = []
    for type in type_list:
        data_type = type["type"]
        index = type["index"]
        if data_type in type_mapping:
            field_defs.append((f"field_{index}", type_mapping[data_type]))

        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    class DynamicStruct(BigEndianStructure):
        _fields_ = field_defs

    return DynamicStruct


def create_fake_dynamic_structure(fields):
    def from_buffer_copy(cls, buffer: io.BytesIO):
        instance = cls()
        for field in fields:
            field_name = f"field_{field.index}"
            field_type = type_mapping.get(field.type, c_bool)
            setattr(
                instance,
                field_name,
                field_type.from_buffer_copy(buffer, field.offset).value,
            )
        return instance

    class_dict = {"from_buffer_copy": classmethod(from_buffer_copy)}

    # Create the class using type()
    dynamic_class = type("FakeDynamicStruct", (object,), class_dict)
    return dynamic_class


class ExcelColumnDefinition(BigEndianStructure):
    _fields_ = (
        ("_type", c_uint16),
        ("offset", c_uint16),
    )
    index: int  # monkey patch assign index

    @classmethod
    def copy(cls, bytes_io) -> "ExcelColumnDefinition":
        return cls.from_buffer_copy(bytes_io.read(sizeof(cls)))

    @property
    def type(self) -> ExcelColumnDataType:
        return ExcelColumnDataType(self._type)

    @property
    def offset(self):
        return self.offset


class ExcelDataPagination(BigEndianStructure):
    _fields_ = (
        ("start_id", c_uint32),
        ("row_count", c_uint32),
    )

    @classmethod
    def copy(cls, bytes_io) -> "ExcelDataPagination":
        return cls.from_buffer_copy(bytes_io.read(sizeof(cls)))

    @property
    def start_id(self) -> int:
        return self.start_id

    @property
    def row_count(self):
        return self.row_count


class ExcelDataHeader(BigEndianStructure):
    index_size: int
    magic: str
    _fields_ = [
        ("magic", c_char * 4),
        ("version", c_uint16),
        ("unknown1", c_uint16),
        ("index_size", c_uint32),
        ("unknown2", c_uint32 * 5),
    ]

    @classmethod
    def copy(cls, bytes_io) -> "ExcelDataHeader":
        return cls.from_buffer_copy(bytes_io.read(sizeof(cls)))


# Structure for ExcelDataOffset
class ExcelDataOffset(BigEndianStructure):
    row_id: int
    offset: int
    _fields_ = [("row_id", c_uint32), ("offset", c_uint32)]

    @classmethod
    def copy(cls, bytes_io) -> "ExcelDataOffset":
        return cls.from_buffer_copy(bytes_io.read(sizeof(cls)))


# Structure for ExcelDataRowHeader
class ExcelDataRowHeader(BigEndianStructure):
    data_size: int
    row_count: int
    _fields_ = [("data_size", c_uint32), ("row_count", c_uint16)]

    @classmethod
    def copy(cls, bytes_io: BytesIO) -> "ExcelDataRowHeader":
        size = sizeof(cls)
        size_without_padding = cls.size_without_padding()
        instance = cls.from_buffer_copy(bytes_io.read(size))
        bytes_io.seek(-(size - size_without_padding), os.SEEK_CUR)
        return instance

    @classmethod
    def size_without_padding(cls) -> int:
        """
        sizeof(cls) == 8 with padding 2
        """
        size_without_padding = sum(
            sizeof(field_type) for field_name, field_type in cls._fields_
        )
        return size_without_padding
