from app.se_string.cursor import SliceCursor
from app.se_string.error import InvalidMacroError, InvalidTextError
from app.se_string.expression import Expression
from app.se_string.macro_kind import MacroKind

MACRO_START = 0x02
MACRO_END = 0x03


class TextPayload:
    def __init__(self, bytes_data):
        self.bytes = bytes_data

    def __eq__(self, other):
        if not isinstance(other, TextPayload):
            return False
        return self.bytes == other.bytes

    def __repr__(self):
        return f"TextPayload({self.bytes})"

    def format(self) -> str:
        try:
            return self.bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise InvalidTextError

    def __str__(self):
        return self.format()


class MacroPayload:
    def __init__(self, kind, bytes_data):
        self.kind = kind
        self.bytes = bytes_data

    def expressions(self):
        return Expressions(self.bytes)

    def __repr__(self):
        return f"MacroPayload({self.kind}, {self.bytes})"

    def format(self) -> str:
        try:
            return f"Macro_{self.kind.name}({self.bytes})"
        except UnicodeDecodeError:
            raise InvalidTextError

    def __str__(self):
        return self.format()


class Expressions:
    def __init__(self, data):
        self.cursor = SliceCursor(data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cursor.eof():
            raise StopIteration

        return Expression.read(self.cursor)


class PayloadReader:
    def __init__(self, data: bytes):
        self.cursor = SliceCursor(data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cursor.eof():
            raise StopIteration

        if self.cursor.peek() == MACRO_START:
            self.cursor.seek(1)

            kind = MacroKind(self.cursor.next())

            expr = Expression.read(self.cursor)
            if not isinstance(expr, Expression) or expr.type != Expression.Type.U32:
                raise InvalidMacroError()

            length = expr.value
            body_length = length  # No need for 16-bit system check in Python

            body = self.cursor.take(body_length)

            if self.cursor.next() != MACRO_END:
                raise InvalidMacroError()

            return MacroPayload(kind, body)

        # Read text until the next macro
        text_bytes = self.cursor.take_until(lambda byte: byte == MACRO_START)
        return TextPayload(text_bytes)
