import io
import os
import zlib
from _ctypes import sizeof

from app import utils
from app.ctype_structure import (
    SqPackHeader,
    IndexHeader,
    IndexFileSegment,
    IndexFolderSegment,
    DataEntryHeader,
    Type2BlockTable,
    BlockHeader,
)


class SQPack:
    folder_path: str
    index_path: str
    index_pack_header: SqPackHeader
    index_header: IndexHeader
    folder_keymap: dict[str, IndexFolderSegment] = {}
    file_keymap: dict[str, IndexFileSegment] = {}
    exd_file = "0a0000.win32"
    files = []

    def __init__(self, folder_path: str):
        self.folder_path = os.path.normpath(os.path.expanduser(folder_path))
        self.index1_path = os.path.join(self.folder_path, f"{self.exd_file}.index")
        self.init_index()
        self.date_path = os.path.join(self.folder_path, f"{self.exd_file}.dat")

        self.init_data()

    @staticmethod
    def print_sqpack_header(header: SqPackHeader):
        print("SqPackHeader:")
        print("Magic:", header.magic.decode("utf-8").strip("\x00"))
        print("Platform ID:", header.platform_id)
        print("Size:", header.size)
        print("Version:", header.version)
        print("Type:", header.type)
        print("SHA1:", bytes(header.sha1).hex())

    @staticmethod
    def print_sqpack_index_header(header: IndexHeader):
        print("\nSqPackIndexHeader:")
        print("Size:", header.header_length)
        print("Type:", header.type)
        print("file segment Offset:", header.file_segment_header.segment_offset)
        print("file segment Size:", header.file_segment_header.segment_offset)
        print("file segment count:", header.folder_segment_header.segment_count)
        print("folder segment Offset:", header.folder_segment_header.segment_offset)
        print("folder segment Size:", header.folder_segment_header.segment_offset)
        print("folder segment count:", header.folder_segment_header.segment_count)

    def init_index(self):
        with open(self.index1_path, "rb") as f:
            # Read the SqPackHeader data
            self.index_pack_header = SqPackHeader.from_buffer_copy(
                f.read(sizeof(SqPackHeader))
            )

            # Read the IndexHeader data
            self.index_header = IndexHeader.from_buffer_copy(
                f.read(sizeof(IndexHeader))
            )
            offset = self.index_header.folder_segment_header.segment_offset
            f.seek(offset)
            for i in range(self.index_header.folder_segment_header.segment_count):
                folder_segment = IndexFolderSegment.from_buffer_copy(
                    f.read(sizeof(IndexFolderSegment))
                )
                self.folder_keymap.update({folder_segment.folder_hash: folder_segment})
            for key in self.folder_keymap.keys():
                folder_segment = self.folder_keymap.get(key)
                offset = folder_segment.files_offset
                folder_segment.file_keymap = {}
                f.seek(offset)
                for i in range(folder_segment.files_count):
                    file_segment = IndexFileSegment.from_buffer_copy(
                        f.read(sizeof(IndexFileSegment))
                    )
                    folder_segment.file_keymap.update(
                        {file_segment.filename_hash: file_segment}
                    )
                    self.file_keymap.update({file_segment.filename_hash: file_segment})

    def init_data(self):
        root_path = "exd/root.exl"
        _folder, file_name = os.path.split(root_path)
        file_segment: IndexFileSegment = self.file_keymap.get(
            utils.compute_crc32(file_name)
        )

        with open(self.date_path + str(file_segment.data_file_id), "rb") as f:
            f.seek(file_segment.offset)
            data_entry_header = DataEntryHeader.from_buffer_copy(
                f.read(sizeof(DataEntryHeader))
            )
            block_tables = []
            for i in range(data_entry_header.num_blocks):
                block_table = Type2BlockTable.from_buffer_copy(
                    f.read(sizeof(Type2BlockTable))
                )
                block_tables.append(block_table)
            end_of_header = file_segment.offset + data_entry_header.header_length
            for block_table in block_tables:
                f.seek(end_of_header + block_table.offset)
                block_header = BlockHeader.from_buffer_copy(f.read(sizeof(BlockHeader)))
                block_size = (
                    block_header.compressed_length
                    if block_header.is_compressed
                    else block_header.decompressed_length
                )
                if (
                    block_header.is_compressed
                    and (block_table.block_size + sizeof(BlockHeader)) % 128 != 0
                ):
                    block_size += 128 - ((block_size + sizeof(BlockHeader)) % 128)
                block_data = f.read(block_table.block_size)
                if block_header.is_compressed:
                    block_data = zlib.decompress(block_data, -zlib.MAX_WBITS)
                bytes_io = io.BytesIO(block_data)

                # Read and print lines one by one
                for line in bytes_io:
                    self.files.append(line)
        pass
