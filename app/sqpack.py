import os
from _ctypes import sizeof

from app.ctype_structure import (
    SqPackHeader,
    IndexHeader,
    IndexFileSegment,
    IndexFolderSegment,
    SqPackDataHeader,
)


class SQPack:
    folder_path: str
    index_path: str
    index_pack_header: SqPackHeader
    index_header: IndexHeader
    folder_keymap: dict[str, IndexFolderSegment] = {}
    file_keymap: dict[str, IndexFileSegment] = {}
    exd_file = "0a0000.win32"

    def read_date_headers(self, file_path: str):
        with open(file_path, "rb") as f:
            # Read the SqPackHeader data
            sqpack_header_data = f.read(sizeof(SqPackHeader))
            sqpack_header = SqPackHeader.from_buffer_copy(sqpack_header_data)

            data_header_data = f.read(sizeof(SqPackDataHeader))
            data_header = SqPackDataHeader.from_buffer_copy(data_header_data)

            return sqpack_header, data_header

    def __init__(self, folder_path: str):
        self.folder_path = os.path.expanduser(folder_path)
        self.index1_path = os.path.normpath(
            self.folder_path + f"/{self.exd_file}.index"
        )
        self.init_index(self.index1_path)
        self.init_data()

        self.date_path = os.path.normpath(self.folder_path + f"/{self.exd_file}.dat{0}")
        self.sqpack_header_data, self.sqpack_data_header = self.read_date_headers(
            self.date_path
        )
        for entry in self.index_file_hash_table_entries:
            entry.offset

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

    def init_index(self, index1_path):
        with open(index1_path, "rb") as f:
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
        pass
