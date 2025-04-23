import io

from app.se_string.error import UnexpectedEOFError


class SliceCursor:
    def __init__(self, data):
        self.buffer = io.BytesIO(data)
        self.data_size = len(data)

    def eof(self):
        return self.buffer.tell() >= self.data_size

    def peek(self) -> int:
        if self.eof():
            raise UnexpectedEOFError()

        current_pos = self.buffer.tell()

        byte = self.buffer.read(1)

        self.buffer.seek(current_pos)

        return byte[0]

    def seek(self, distance):
        self.buffer.seek(distance, io.SEEK_CUR)

    def next(self) -> int:
        if self.eof():
            raise UnexpectedEOFError()

        byte = self.buffer.read(1)

        return byte[0]

    def take(self, count) -> bytes:
        if self.buffer.tell() + count > self.data_size:
            raise UnexpectedEOFError()

        value = self.buffer.read(count)

        if len(value) < count:
            raise UnexpectedEOFError()

        return value

    def take_until(self, predicate):
        result = bytearray()

        while not self.eof():
            pos_before_read = self.buffer.tell()
            byte = self.buffer.read(1)

            if not byte:
                break

            if predicate(byte[0]):
                self.buffer.seek(pos_before_read)
                break

            result.extend(byte)

        return bytes(result)

    def get_offset(self):
        return self.buffer.tell()

    def get_all(self):
        return self.buffer.read()

    def __repr__(self):
        return f"SliceCursor(size={self.data_size}, offset={self.buffer.tell()})"
