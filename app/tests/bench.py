import glob
import json
import os
import io

from orjson import orjson


def __write_with_default_buffer(content, repeat, buffer_size=8192 * 2):
    file_path = "default_buffer_test.txt"
    with open(file_path, "w", buffering=buffer_size) as file:
        for _ in range(repeat):
            file.write(content)

    os.remove(file_path)


def __write_with_custom_buffer(content, repeat, buffer_size=8192 * 2):
    file_path = "custom_buffer_test.txt"

    with open(file_path, "wb", buffering=0) as file:
        buffer = io.BufferedWriter(file, buffer_size=buffer_size)
        for _ in range(repeat):
            buffer.write(content.encode("utf-8"))
        buffer.flush()
    os.remove(file_path)


def test_file_buffer(benchmark):
    content = "a" * 1024  # 1K
    repeat = 1024 * 20  #  20M
    benchmark(__write_with_default_buffer, content, repeat)


def test_custom_file_buffer(benchmark):
    content = "a" * 1024  # 1K
    repeat = 1024 * 20  # 20M

    benchmark(__write_with_custom_buffer, content, repeat)


def test_load_definitions_json(benchmark):
    def load_definitions_json():
        for file_path in glob.glob(os.path.normpath("./Definitions/*.json")):
            with open(file_path, "r") as file:
                def_json = file.read()
                json.loads(def_json)

    benchmark(load_definitions_json)


def test_load_definitions_orjson(benchmark):
    def load_definitions_orjson():
        for file_path in glob.glob(os.path.normpath("./Definitions/*.json")):
            with open(file_path, "r") as file:
                def_json = file.read()
                orjson.loads(def_json)

    benchmark(load_definitions_orjson)
