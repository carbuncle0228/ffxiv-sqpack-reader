import hashlib
import os


def calculate_sha1(file_path, start, length):
    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read(length)
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()


def calculate_sha1_to_eof(file_path, start):
    with open(file_path, "rb") as f:
        f.seek(start)
        data = f.read()
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()


def calculate_size(file_path, start):
    with open(file_path, "rb") as f:
        # Move the cursor to the end of the file
        f.seek(start, os.SEEK_END)

        # Get the current position of the cursor, which is the file size
        file_size = f.tell()
    return file_size
