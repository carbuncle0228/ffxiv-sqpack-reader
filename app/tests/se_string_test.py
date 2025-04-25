import random

from app.se_string import SeString, SliceCursor
from app.se_string.evaluator import (  # noqa for evaluated_value after
    evaluated_se_string,
    expression,
    macro,
)
from app.se_string.packed import get_packed_u32_bytes


def test_se_string():
    str_bytes = b'Delivers an attack with a potency of \x02\x08?\xe4\xe9E\x14\xff"\x02\x08\x1e\xe0\xe9I_\xf0\xdc\xff\x16\x02\x08\x12\xe4\xe9E\x14\xff\x0b\x02\x08\x07\xe0\xe9IU\xc9\x97\x03\x97\x03\x03\xff\x16\x02\x08\x12\xe4\xe9E\x14\xff\x0b\x02\x08\x07\xe0\xe9IU\xc9\x97\x03\x97\x03\x03.'
    se_string = SeString(str_bytes)
    s = str(se_string)
    assert (
        s
        == """Delivers an attack with a potency of {macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 94)),expression("U32Packed", 220),expression("SeString", macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 84)),expression("U32", 200),expression("U32", 150)])),expression("U32", 150)]))])),expression("SeString", macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 84)),expression("U32", 200),expression("U32", 150)])),expression("U32", 150)]))])}."""
    )
    s = """Delivers an attack with a potency of {macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 94)),expression("U32Packed", 220),expression("SeString", macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 84)),expression("U32", 200),expression("U32", 150)])),expression("U32", 150)]))])),expression("SeString", macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 84)),expression("U32", 200),expression("U32", 150)])),expression("U32", 150)]))])}."""

    evaluated_value = evaluated_se_string(s)

    assert (
        evaluated_value
        == """Delivers an attack with a potency of <hex:02083FE4E94514FF2202081EE0E9495FF0DCFF16020812E4E94514FF0B020807E0E94955C99703970303FF16020812E4E94514FF0B020807E0E94955C99703970303>."""
    )


def test_direct_evaluator_macro():
    bytes_ = macro(
        "IF",
        [
            expression(
                "Eq",
                expression("GlobalNumber", expression("U32", 68)),
                expression("U32", 19),
            ),
            expression(
                "SeString",
                macro(
                    "IF",
                    [
                        expression(
                            "Ge",
                            expression("GlobalNumber", expression("U32", 72)),
                            expression("U32", 94),
                        ),
                        expression("U32Packed", 220),
                        expression(
                            "SeString",
                            macro(
                                "IF",
                                [
                                    expression(
                                        "Eq",
                                        expression(
                                            "GlobalNumber", expression("U32", 68)
                                        ),
                                        expression("U32", 19),
                                    ),
                                    expression(
                                        "SeString",
                                        macro(
                                            "IF",
                                            [
                                                expression(
                                                    "Ge",
                                                    expression(
                                                        "GlobalNumber",
                                                        expression("U32", 72),
                                                    ),
                                                    expression("U32", 84),
                                                ),
                                                expression("U32", 200),
                                                expression("U32", 150),
                                            ],
                                        ),
                                    ),
                                    expression("U32", 150),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            expression(
                "SeString",
                macro(
                    "IF",
                    [
                        expression(
                            "Eq",
                            expression("GlobalNumber", expression("U32", 68)),
                            expression("U32", 19),
                        ),
                        expression(
                            "SeString",
                            macro(
                                "IF",
                                [
                                    expression(
                                        "Ge",
                                        expression(
                                            "GlobalNumber", expression("U32", 72)
                                        ),
                                        expression("U32", 84),
                                    ),
                                    expression("U32", 200),
                                    expression("U32", 150),
                                ],
                            ),
                        ),
                        expression("U32", 150),
                    ],
                ),
            ),
        ],
    )
    hex_str = f"<hex:{''.join(f'{b:02X}' for b in bytes_)}>"

    assert (
        hex_str
        == "<hex:02083FE4E94514FF2202081EE0E9495FF0DCFF16020812E4E94514FF0B020807E0E94955C99703970303FF16020812E4E94514FF0B020807E0E94955C99703970303>"
    )


def test_packed_u32():
    def read_packed_u32(cursor_bytes_: bytes, kind: int) -> int:
        cursor = SliceCursor(cursor_bytes_)
        f"{kind + 1:b}"
        f"{0xF0:b}"
        f"{0xFE:b}"
        flags = (kind + 1) & 0b1111
        bytes_ = [0] * 4
        for i in reversed(range(4)):
            if flags & (1 << i):
                bytes_[i] = cursor.next() or 0
        return int.from_bytes(bytes_, "little")

    max_u32 = (1 << 32) - 1
    test_value = [max_u32, 0, random.choice(range(max_u32))]
    for i in test_value:
        packed_u32 = get_packed_u32_bytes(i)
        kind = packed_u32[0]
        cursor_bytes = packed_u32[1:]
        res = read_packed_u32(cursor_bytes, kind)
        assert res == i
