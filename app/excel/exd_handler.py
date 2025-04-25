import csv
import os
from _ctypes import sizeof

from app import utils
from app.config import settings
from app.ctype_structure import (
    ExcelColumnDataType,
    ExcelDataHeader,
    ExcelDataOffset,
    ExcelDataRowHeader,
    ExcelVariant,
    IndexFileSegment,
    create_dynamic_structure,
    create_fake_dynamic_structure,
)
from app.excel import ex_header, read_file_data
from app.model import Languages
from app.se_string import SeString
from app.sqpack import SQPack


def write_csv(sqpack: SQPack, target_folder, file_path):
    if file_path not in {"Addon", "ActionTransient"} and settings.DEBUG_SKIP:
        return  # TODO debug
    target_path = os.path.join(
        target_folder, os.path.normpath(f"rawexd/{file_path}.csv")
    )
    exh_header, data_pagination, columns = ex_header.read_file_header(sqpack, file_path)
    if settings.ONLY_STR_MODE and exh_header.language_count <= 1:
        return  # only write file have multiple language
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", buffering=1024 * 1024 * 8, encoding="utf-8") as file:
        csv_writer = csv.writer(file, delimiter=",")
        key_row = ["key"]
        header_row = ["#"]
        offset_row = ["offset"]
        type_row = ["int32"]
        sheet_map = sqpack.definition.sheet_map.get(file_path)
        column_index_to_name_map = (
            sheet_map.column_index_to_name_map if sheet_map else {}
        )
        for i, column in enumerate(columns):
            if settings.ONLY_STR_MODE and column.type.name != "String":
                continue  # only string
            key_row += [f"{i}"]
            header_row += [f"{column_index_to_name_map.get(i, '')}"]
            offset_row += [f"{column.offset}"]
            type_row += [f"{column.type.name}"]
        csv_writer.writerow(key_row)
        csv_writer.writerow(header_row)
        csv_writer.writerow(offset_row)
        csv_writer.writerow(type_row)

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

            exd_key_list = [
                ExcelDataOffset.copy(bytes_io)
                for _ in range(exd_header.index_size // sizeof(ExcelDataOffset))
            ]
            bytes_io.seek(exd_key_list[0].offset)
            data_size = exh_header.data_offset
            ColumnStruct = create_dynamic_structure(
                [
                    {"type": column.type, "index": column.index}
                    for column in sorted_columns
                ]
            )
            if sizeof(ColumnStruct) > data_size:
                ColumnStruct = create_fake_dynamic_structure(columns)
            if exh_header.variant_name == ExcelVariant.Default:
                for i in range(exd_header.index_size // sizeof(ExcelDataOffset)):
                    exd_row = [f"{exd_key_list[i].row_id}"]
                    exd_row_header = ExcelDataRowHeader.copy(bytes_io)
                    fixed_data = bytes_io.read(data_size)
                    column_struct = ColumnStruct.from_buffer_copy(fixed_data)
                    str_size = exd_row_header.data_size - data_size
                    bytes_str = bytes_io.read(str_size)
                    # b'To Crush Your Enemies I\x00Defeat 100 enemies.\x00\x00\x00' -> string column spilts by \x00
                    str_columns: list[bytes] = bytes_str.split(b"\x00")
                    current_string_index = 0
                    for j, column in enumerate(columns):
                        if column.type == ExcelColumnDataType.String:
                            str_column = str_columns[current_string_index]
                            if b"\02" in str_column:
                                parsed_str = str(SeString(str_column))
                                exd_row += [f"{parsed_str}"]
                            else:
                                exd_row += [f"{str_column.decode('utf-8')}"]
                            current_string_index += 1
                        elif settings.ONLY_STR_MODE:
                            # only write string skip other type
                            continue
                        elif (
                            "PackedBool" in column.type.name
                            and type(column_struct).__name__ == "DynamicStruct"
                        ):
                            exd_row += [f"{getattr(column_struct, f'field_{j}').value}"]
                        else:
                            exd_row += [f"{getattr(column_struct, f'field_{j}')}"]
                    csv_writer.writerow(exd_row)

            else:
                pass
