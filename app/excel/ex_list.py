from app.excel import read_file_data


def read_file_list(file_segment, data_path):
    with open(data_path + str(file_segment.data_file_id), "rb") as f:
        bytes_io = read_file_data(f, file_segment)

    return bytes_io
