import os
from _ctypes import sizeof
from datetime import datetime

from app import utils
from app.ctype_structure import (
    IndexFileSegment,
    IndexFolderSegment,
    IndexHeader,
    SqPackHeader,
)
from app.excel import ex_list
from app.excel.definition import RelationDefinition


class SQPack:
    folder_path: str
    sqpack_path: str
    index_path: str
    data_path: str
    game_version: str
    index_pack_header: SqPackHeader
    index_header: IndexHeader
    folder_keymap: dict[str, IndexFolderSegment] = {}
    file_keymap: dict[str, IndexFileSegment] = {}
    exd_file = "0a0000.win32"
    files: dict[str, int] = {}
    definition: RelationDefinition

    def __init__(self, folder_path: str):
        self.folder_path = os.path.normpath(os.path.expanduser(folder_path))
        version_file_path = os.path.join(self.folder_path, "game", "ffxivgame.ver")
        if os.path.exists(version_file_path):
            with open(version_file_path, "rb") as version_file:
                self.game_version = version_file.read().decode("utf-8")
        else:
            self.game_version = f"{datetime.now():%Y%m%d%H%M%S}"
        if os.path.exists(os.path.join(self.folder_path, "0a0000.win32.index")):
            self.sqpack_path = self.folder_path
        else:
            self.sqpack_path = os.path.join(self.folder_path, "game", "sqpack", "ffxiv")
        self.index_path = os.path.join(self.sqpack_path, f"{self.exd_file}.index")
        self.init_index()
        self.data_path = os.path.join(self.sqpack_path, f"{self.exd_file}.dat")

        self.init_data()
        self.init_def()

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
        with open(self.index_path, "rb") as f:
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

        file_segment: IndexFileSegment = utils.get_file(self.file_keymap, root_path)
        bytes_io = ex_list.read_file_list(file_segment, self.data_path)
        bytes_io.readline()  # skip header EXLT,2
        for line in bytes_io:
            file, id = str(line.strip().decode("utf-8")).split(",")
            self.files.update({file: int(id)})

    def init_def(self):
        self.definition = RelationDefinition()
