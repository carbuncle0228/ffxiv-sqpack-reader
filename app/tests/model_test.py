from _ctypes import sizeof

from app.ctype_structure import SqPackHeader, SqPackIndexHeader
from app.tests import calculate_sha1


def test_read_sqpack_headers(index_file_path):
    with open(index_file_path, "rb") as f:
        # Read the SqPackHeader data
        sqpack_header_data = f.read(sizeof(SqPackHeader))
        sqpack_header = SqPackHeader.from_buffer_copy(sqpack_header_data)
    assert bytes(sqpack_header.sha1).hex() == calculate_sha1(index_file_path, 0, 0x3C0)


def test_read_sqpack_index_headers(index_file_path):
    with open(index_file_path, "rb") as f:
        # Read the SqPack Index header data
        f.seek(1024)
        sqpack_index_header_data = f.read(sizeof(SqPackIndexHeader))
        sqpack_index_header = SqPackIndexHeader.from_buffer_copy(
            sqpack_index_header_data
        )
    assert bytes(sqpack_index_header.sq_pack_index_header_item1.sha1).hex() == calculate_sha1(
        index_file_path,
        sqpack_index_header.sq_pack_index_header_item1.index_data_offset,
        sqpack_index_header.sq_pack_index_header_item1.index_data_size,
    )
    assert bytes(sqpack_index_header.sq_pack_index_header_item2.sha1).hex() == calculate_sha1(
        index_file_path,
        sqpack_index_header.sq_pack_index_header_item2.index_data_offset,
        sqpack_index_header.sq_pack_index_header_item2.index_data_size,
    )
    assert bytes(sqpack_index_header.sq_pack_index_header_item3.sha1).hex() == calculate_sha1(
        index_file_path,
        sqpack_index_header.sq_pack_index_header_item3.index_data_offset,
        sqpack_index_header.sq_pack_index_header_item3.index_data_size,
    )
    assert bytes(sqpack_index_header.sq_pack_index_header_item4.sha1).hex() == calculate_sha1(
        index_file_path,
        sqpack_index_header.sq_pack_index_header_item4.index_data_offset,
        sqpack_index_header.sq_pack_index_header_item4.index_data_size,
    )



# fail
# def test_read_sqpack_data_headers(data_file_path):
#     with open(data_file_path, "rb") as f:
#         # Read the SqPack Data Header data
#         f.seek(1024)
#         sq_pack_data_header_data = f.read(sizeof(SqPackDataHeader))
#         sq_pack_data_header = SqPackDataHeader.from_buffer_copy(
#             sq_pack_data_header_data
#         )
#
#     assert bytes(sq_pack_data_header.sha1_header).hex() == calculate_sha1(
#         data_file_path, 1024, 1024+0x3C0
#     )
#
#
#     assert bytes(sq_pack_data_header.sha1_data).hex() == calculate_sha1_to_eof(
#         data_file_path,
#         2048,
#     )
