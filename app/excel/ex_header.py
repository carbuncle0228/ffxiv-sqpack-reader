from app import utils
from app.ctype_structure import (
    ExhHeader,
    ExcelColumnDefinition,
    ExcelDataPagination,
    IndexFileSegment,
)
from app.excel import read_file_data
from app.sqpack import SQPack

aaa = []


def read_file_header(sq_pack: SQPack, file_path: str):
    exh_path = f"exd/{file_path}.exh"
    file_segment: IndexFileSegment = utils.get_file(sq_pack.file_keymap, exh_path)
    with open(sq_pack.data_path + str(file_segment.data_file_id), "rb") as f:
        bytes_io = read_file_data(f, file_segment)

    exh_header = ExhHeader.copy(bytes_io)
    columns = []
    for i in range(exh_header.column_count):
        exh_header_column_define = ExcelColumnDefinition.copy(bytes_io)
        exh_header_column_define.index = i
        columns.append(exh_header_column_define)

    data_pagination = ExcelDataPagination.copy(bytes_io)
    return exh_header, data_pagination, columns
