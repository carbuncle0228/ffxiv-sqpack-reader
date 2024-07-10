from _ctypes import sizeof

from app.ctype_structure import ExhHeader, ExcelColumnDefinition
from app.excel import read_file_data


def read_file_header(file_segment, data_path):
    with open(data_path + str(file_segment.data_file_id), "rb") as f:
        bytes_io = read_file_data(f, file_segment)

    exh_header = ExhHeader.from_buffer_copy(bytes_io.getvalue())
    bytes_io.seek(sizeof(ExhHeader))
    columns = []
    for i in range(exh_header.column_count):
        exh_header_column_define = ExcelColumnDefinition.from_buffer_copy(
            bytes_io.read(sizeof(ExcelColumnDefinition))
        )
        columns.append(exh_header_column_define)

    return exh_header
