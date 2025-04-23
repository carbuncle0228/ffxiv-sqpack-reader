from enum import Enum
from typing import Optional, Union

from app import se_string
from app.se_string import cursor
from app.se_string.error import InvalidExpressionError


class Expression:
    class Type(Enum):
        U32 = "U32"
        SeString = "SeString"
        Millisecond = "Millisecond"
        Second = "Second"
        Minute = "Minute"
        Hour = "Hour"
        Day = "Day"
        Weekday = "Weekday"
        Month = "Month"
        Year = "Year"
        StackColor = "StackColor"
        LocalNumber = "LocalNumber"
        GlobalNumber = "GlobalNumber"
        LocalString = "LocalString"
        GlobalString = "GlobalString"
        Ge = "Ge"
        Gt = "Gt"
        Le = "Le"
        Lt = "Lt"
        Eq = "Eq"
        Ne = "Ne"
        Unknown = "Unknown"

    def __init__(
        self,
        type_: Type,
        value: Optional[
            Union[int, "Expression", "se_string.SeString", tuple, bytes]
        ] = None,
    ):
        self.type = type_
        self.value = value

    @classmethod
    def read(cls, cursor: cursor.SliceCursor):
        kind = cursor.next()
        if kind is None:
            raise InvalidExpressionError

        def read_inner():
            return cls.read(cursor)

        if 0x01 <= kind <= 0xCF:
            return cls(cls.Type.U32, kind - 1)
        elif kind == 0xD8:
            return cls(cls.Type.Millisecond)
        elif kind == 0xD9:
            return cls(cls.Type.Second)
        elif kind == 0xDA:
            return cls(cls.Type.Minute)
        elif kind == 0xDB:
            return cls(cls.Type.Hour)
        elif kind == 0xDC:
            return cls(cls.Type.Day)
        elif kind == 0xDD:
            return cls(cls.Type.Weekday)
        elif kind == 0xDE:
            return cls(cls.Type.Month)
        elif kind == 0xDF:
            return cls(cls.Type.Year)
        elif kind == 0xE0:
            return cls(cls.Type.Ge, (read_inner(), read_inner()))
        elif kind == 0xE1:
            return cls(cls.Type.Gt, (read_inner(), read_inner()))
        elif kind == 0xE2:
            return cls(cls.Type.Le, (read_inner(), read_inner()))
        elif kind == 0xE3:
            return cls(cls.Type.Lt, (read_inner(), read_inner()))
        elif kind == 0xE4:
            return cls(cls.Type.Eq, (read_inner(), read_inner()))
        elif kind == 0xE5:
            return cls(cls.Type.Ne, (read_inner(), read_inner()))
        elif kind == 0xE8:
            return cls(cls.Type.LocalNumber, read_inner())
        elif kind == 0xE9:
            return cls(cls.Type.GlobalNumber, read_inner())
        elif kind == 0xEA:
            return cls(cls.Type.LocalString, read_inner())
        elif kind == 0xEB:
            return cls(cls.Type.GlobalString, read_inner())
        elif kind == 0xEC:
            return cls(cls.Type.StackColor)
        elif 0xF0 <= kind <= 0xFE:
            return cls(cls.Type.U32, read_packed_u32(cursor, kind))
        elif kind == 0xFF:
            return cls(
                cls.Type.SeString,
                se_string.SeString(cursor.take(count=cursor.data_size)),
            )
        else:
            return cls(cls.Type.Unknown, kind)


def read_packed_u32(cursor: se_string.cursor.SliceCursor, kind: int) -> int:
    flags = (kind + 1) & 0b1111
    bytes_ = [0] * 4
    for i in reversed(range(4)):
        if flags & (1 << i):
            bytes_[i] = cursor.next() or 0
    return int.from_bytes(bytes_, "little")


def read_bytes(cursor: se_string.cursor.SliceCursor, kind: int) -> bytes:
    return bytes([kind]) + cursor.get_all()


def read_inline_sestring(cursor: se_string.cursor.SliceCursor) -> se_string.SeString:
    expr = Expression.read(cursor)
    if not isinstance(expr, Expression) or expr.type != Expression.Type.U32:
        raise InvalidExpressionError
    string_length = expr.value
    string_data = cursor.take(string_length)
    return se_string.SeString(string_data)
