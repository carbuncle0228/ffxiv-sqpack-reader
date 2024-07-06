import io
import zlib
from _ctypes import sizeof

from app.ctype_structure import DataEntryHeader, Type2BlockTable, BlockHeader


def read_file_list(file_segment, date_path):
    bytes_io = io.BytesIO()

    with open(date_path + str(file_segment.data_file_id), "rb") as f:
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
            block_header = BlockHeader.from_buffer_copy(f.read(BlockHeader.sizeof()))
            block_size = (
                block_header.compressed_length
                if block_header.is_compressed
                else block_header.decompressed_length
            )
            if (
                block_header.is_compressed
                and (block_table.block_size + BlockHeader.sizeof()) % 128 != 0
            ):
                block_size += 128 - ((block_size + BlockHeader.sizeof()) % 128)
            block_data = f.read(block_table.block_size)
            if block_header.is_compressed:
                block_data = zlib.decompress(block_data, -zlib.MAX_WBITS)
            bytes_io.write(block_data)

    return bytes_io
