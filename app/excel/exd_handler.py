import os
from _ctypes import sizeof

from app import utils
from app.config import settings
from app.ctype_structure import (
    create_dynamic_structure,
    IndexFileSegment,
    ExcelDataHeader,
    ExcelDataOffset,
    ExcelVariant,
    ExcelDataRowHeader, ExcelColumnDataType, create_fake_dynamic_structure,
)
from app.excel import ex_header, read_file_data
from app.model import Languages
from app.sqpack import SQPack


def write_csv(sqpack: SQPack, target_folder, file_path):
    target_path = os.path.join(
        target_folder, os.path.normpath(f"rawexd/{file_path}.csv")
    )
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", buffering=1024 * 1024 * 8) as file:
        exh_header, data_pagination, columns = ex_header.read_file_header(
            sqpack, file_path
        )
        key_str = "key"
        header_str = "#"
        offset_str = "offset"
        type_str = "int32"
        sheet_map = sqpack.definition.sheet_map.get(
            file_path
        )
        column_index_to_name_map = sheet_map.column_index_to_name_map if sheet_map else {}
        for i, column in enumerate(columns):
            key_str += f",{i}"
            header_str += f",{column_index_to_name_map.get(i,"")}"
            offset_str += f",{column.offset}"
            type_str += f",{column.type.name}"
        file.writelines(
            [key_str, "\n", header_str, "\n", offset_str, "\n", type_str, "\n"]
        )
        sorted_columns = sorted(columns, key=lambda c: c.offset)

        if exh_header.language_count > 1:
            data_path = f"exd/{file_path}_{data_pagination.start_id}_{Languages[settings.language].value}.exd"
        else:
            data_path = f"exd/{file_path}_{data_pagination.start_id}.exd"
        file_segment: IndexFileSegment = utils.get_file(sqpack.file_keymap, data_path)
        with open(sqpack.data_path + str(file_segment.data_file_id), "rb") as f:
            bytes_io = read_file_data(f, file_segment)
            exd_header = ExcelDataHeader.copy(bytes_io)
            if exd_header.index_size == 0:
                return
            exd_offset = ExcelDataOffset.copy(bytes_io)
            bytes_io.seek(exd_offset.offset)
            data_size = exh_header.data_offset
            ColumnStruct = create_dynamic_structure(
                [{"type": column.type, "index": column.index} for column in sorted_columns]
            )
            if sizeof(ColumnStruct)> data_size:
                ColumnStruct = create_fake_dynamic_structure(columns)
            if exh_header.variant_name == ExcelVariant.Default:
                for i in range(exd_header.index_size // sizeof(ExcelDataOffset)):
                    row_str = f"{i}"
                    exd_row_header = ExcelDataRowHeader.copy(bytes_io)
                    fixed_data = bytes_io.read(data_size)
                    column_struct = ColumnStruct.from_buffer_copy(fixed_data)
                    str_size = exd_row_header.data_size - data_size
                    bytes_str = bytes_io.read(str_size)
                    str_for_columns = bytes_str.split(b"\x00")
                    current_string = 0
                    for j, column in enumerate(columns):
                        if column.type == ExcelColumnDataType.String:
                            if b"\02" in str_for_columns[current_string]:
                                row_str += f",TODOEncode"
                            else:
                                row_str += f",{str_for_columns[current_string].decode("utf-8")}"  # todo add ffxiv string decorder
                            current_string +=1
                        elif "PackedBool" in column.type.name and type(column_struct).__name__ == "DynamicStruct" :
                            row_str += f",{getattr(column_struct, f"field_{j}").value}"
                        else:
                            row_str += f",{getattr(column_struct, f"field_{j}")}"
                    file.writelines(
                        [row_str, "\n", ]
                    )


            else:
                pass
