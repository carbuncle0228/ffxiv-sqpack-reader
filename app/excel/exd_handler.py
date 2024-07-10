import os

from app import utils
from app.ctype_structure import IndexFileSegment
from app.excel import ex_header


def write_csv(sqpack, target_folder, file_path):
    target_path = os.path.join(
        target_folder, os.path.normpath(f"rawexd/{file_path}.csv")
    )
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as file:
        exh_path = f"exd/{file_path}.exh"

        file_segment: IndexFileSegment = utils.get_file(sqpack, exh_path)
        header = ex_header.read_file_header(file_segment, sqpack.data_path)
        file.write("Hello, world!")
