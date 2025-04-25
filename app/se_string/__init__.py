import logging
from typing import Optional, Union

from app.config import settings
from app.se_string.cursor import SliceCursor
from app.se_string.error import (
    InvalidExpressionError,
    InvalidMacroError,
    InvalidTextError,
    SeStringError,
)
from app.se_string.packed import get_length_bytes_str
from app.se_string.type import ExpressionType, MacroKind


class SeString:
    """
    Square Enix rich text format (SeString).
    """

    def __init__(self, data: bytes):
        self.data = data

    def payloads(self):
        reader = PayloadReader(self.data)
        try:
            return [payload for payload in reader]
        except Exception as e:
            logging.exception(e, exc_info=True)
            raise e

    def format(self) -> str:
        reader = PayloadReader(self.data)

        try:
            return "".join(str(payload) for payload in reader)
        except SeStringError as e:
            logging.exception(e, exc_info=True)
            if settings.SKIP_ERROR:
                return "invalid SeString"
            else:
                raise e
        except Exception as e:
            logging.exception(e, exc_info=True)
            if settings.SKIP_ERROR:
                return "parse error"
            else:
                raise e

    def __str__(self):
        return self.format()


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

    def args(self):
        return SliceCursor(self.bytes)

    def __repr__(self):
        return f"MacroPayload({self.kind}, {self.bytes})"

    def format(self) -> str:
        try:
            return self.format_macro()

        except UnicodeDecodeError:
            raise InvalidTextError

    def __str__(self):
        return self.format()

    def __format_hex(self):
        content = "".join(f"{b:02X}" for b in self.bytes) if self.bytes else ""

        return f"<hex:02{self.kind.value:02X}{get_length_bytes_str(self.bytes)}{content}03>"

    def format_macro(self):
        if settings.HEX_STR_MODE:
            return self.__format_hex()
        if self.kind == MacroKind.SWITCH:
            return self.__format_hex()
        reader = MacroExpressionReader(self.bytes)

        args = ",".join(str(arg) for arg in reader)

        return f'{{macro("{self.kind.name}", [{args}])}}'


MACRO_START = 0x02
MACRO_END = 0x03


class PayloadReader:
    def __init__(self, data: bytes):
        self.cursor = SliceCursor(data)

    def __iter__(self):
        return self

    def payload_length_reader(self):
        kind = self.cursor.next()
        if kind is None:
            raise InvalidExpressionError

        if 0x01 <= kind <= 0xCF:
            return Expression(ExpressionType.U32, kind - 1)

        elif 0xF0 <= kind <= 0xFE:
            return Expression(
                ExpressionType.U32Packed, self.cursor.read_packed_u32(kind)
            )

        else:
            raise InvalidExpressionError()

    def __next__(self):
        if self.cursor.eof():
            raise StopIteration

        if self.cursor.peek() == MACRO_START:
            self.cursor.seek(1)

            kind = MacroKind(self.cursor.next())

            expr = self.payload_length_reader()
            if not isinstance(expr, Expression):
                raise InvalidMacroError()

            length = expr.value
            body_length = length

            body = self.cursor.take(body_length)

            if self.cursor.next() != MACRO_END:
                raise InvalidMacroError()

            return MacroPayload(kind, body)

        # Read text until the next macro
        text_bytes = self.cursor.take_until(lambda byte: byte == MACRO_START)
        return TextPayload(text_bytes)


class Expression:
    def __init__(
        self,
        type_: ExpressionType,
        value: Optional[
            Union[int, "Expression", SeString, tuple["Expression", "Expression"], bytes]
        ] = None,
    ):
        self.type = type_
        self.value = value

    def format(self) -> str:
        match self.type:
            case ExpressionType.U32:
                return f'expression("{self.type.name}", {self.value})'
            case ExpressionType.U32Packed:
                return f'expression("{self.type.name}", {self.value})'
            case ExpressionType.Millisecond:
                return f'expression("{self.type.name}")'
            case ExpressionType.Second:
                return f'expression("{self.type.name}")'
            case ExpressionType.Minute:
                return f'expression("{self.type.name}")'
            case ExpressionType.Hour:
                return f'expression("{self.type.name}")'
            case ExpressionType.Day:
                return f'expression("{self.type.name}")'
            case ExpressionType.Weekday:
                return f'expression("{self.type.name}")'
            case ExpressionType.Month:
                return f'expression("{self.type.name}")'
            case ExpressionType.Year:
                return f'expression("{self.type.name}")'
            case ExpressionType.Ge:
                return (
                    f'expression("{self.type.name}", {self.value[0]}, {self.value[1]})'
                )
            case ExpressionType.Gt:
                return (
                    f'expression("{self.type.name}", {self.value[0]}, {self.value[1]})'
                )
            case ExpressionType.Le:
                return (
                    f'expression("{self.type.name}", {self.value[0]}, {self.value[1]})'
                )
            case ExpressionType.Lt:
                return (
                    f'expression("{self.type.name}", {self.value[0]}, {self.value[1]})'
                )
            case ExpressionType.Eq:
                return (
                    f'expression("{self.type.name}", {self.value[0]}, {self.value[1]})'
                )
            case ExpressionType.Ne:
                return (
                    f'expression("{self.type.name}", {self.value[0]}, {self.value[1]})'
                )
            case ExpressionType.LocalNumber:
                return f'expression("{self.type.name}", {self.value})'
            case ExpressionType.GlobalNumber:
                return f'expression("{self.type.name}", {self.value})'
            case ExpressionType.LocalString:
                return f'expression("{self.type.name}", {self.value})'
            case ExpressionType.GlobalString:
                return f'expression("{self.type.name}", {self.value})'
            case ExpressionType.StackColor:
                return f'expression("{self.type.name}")'
            case ExpressionType.SeString:
                return f'expression("{self.type.name}", {self.value})'
            case _:
                return f'expression("{self.type.name}", {self.value})'

    def __str__(self):
        return self.format()


class MacroExpressionReader:
    def __init__(self, data: bytes | SliceCursor):
        self.cursor = SliceCursor(data)

    def __iter__(self):
        return self

    def read(self) -> Expression:
        kind = self.cursor.next()
        if kind is None:
            raise InvalidExpressionError

        def read_inner() -> Expression:
            return self.read()

        if 0x01 <= kind <= 0xCF:
            return Expression(ExpressionType.U32, kind - 1)
        elif kind == 0xD8:
            return Expression(ExpressionType.Millisecond)
        elif kind == 0xD9:
            return Expression(ExpressionType.Second)
        elif kind == 0xDA:
            return Expression(ExpressionType.Minute)
        elif kind == 0xDB:
            return Expression(ExpressionType.Hour)
        elif kind == 0xDC:
            return Expression(ExpressionType.Day)
        elif kind == 0xDD:
            return Expression(ExpressionType.Weekday)
        elif kind == 0xDE:
            return Expression(ExpressionType.Month)
        elif kind == 0xDF:
            return Expression(ExpressionType.Year)
        elif kind == 0xE0:
            return Expression(ExpressionType.Ge, (read_inner(), read_inner()))
        elif kind == 0xE1:
            return Expression(ExpressionType.Gt, (read_inner(), read_inner()))
        elif kind == 0xE2:
            return Expression(ExpressionType.Le, (read_inner(), read_inner()))
        elif kind == 0xE3:
            return Expression(ExpressionType.Lt, (read_inner(), read_inner()))
        elif kind == 0xE4:
            return Expression(ExpressionType.Eq, (read_inner(), read_inner()))
        elif kind == 0xE5:
            return Expression(ExpressionType.Ne, (read_inner(), read_inner()))
        elif kind == 0xE8:
            return Expression(ExpressionType.LocalNumber, read_inner())
        elif kind == 0xE9:
            return Expression(ExpressionType.GlobalNumber, read_inner())
        elif kind == 0xEA:
            return Expression(ExpressionType.LocalString, read_inner())
        elif kind == 0xEB:
            return Expression(ExpressionType.GlobalString, read_inner())
        elif kind == 0xEC:
            return Expression(ExpressionType.StackColor)
        elif 0xF0 <= kind <= 0xFE:
            return Expression(
                ExpressionType.U32Packed, self.cursor.read_packed_u32(kind)
            )
        elif kind == 0xFF:
            return Expression(
                ExpressionType.SeString,
                self.read_inline_sestring(),
            )
        else:
            return Expression(ExpressionType.Unknown, kind)

    def read_bytes(self, kind: int) -> bytes:
        return bytes([kind]) + self.cursor.get_all()

    def read_inline_sestring(self) -> SeString:
        expr = self.read()
        if not isinstance(expr, Expression) or expr.type not in (
            ExpressionType.U32,
            ExpressionType.U32Packed,
        ):
            raise InvalidExpressionError
        string_length = expr.value
        string_data = self.cursor.take(string_length)

        return SeString(string_data)

    def __next__(self):
        if self.cursor.eof():
            raise StopIteration
        expr = self.read()
        return expr
