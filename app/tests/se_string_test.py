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
        == """Delivers an attack with a potency of {macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", [macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 94)),expression("U32Packed", 220),expression("SeString", [macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", [macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 84)),expression("U32", 200),expression("U32", 150)])]),expression("U32", 150)])])])]),expression("SeString", [macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", [macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 84)),expression("U32", 200),expression("U32", 150)])]),expression("U32", 150)])])], to_hex=True)}."""
    )

    evaluated_value = evaluated_se_string(s)

    assert (
        evaluated_value
        == """Delivers an attack with a potency of <hex:02083FE4E94514FF2202081EE0E9495FF0DCFF16020812E4E94514FF0B020807E0E94955C99703970303FF16020812E4E94514FF0B020807E0E94955C99703970303>."""
    )
    "02083FE4E94514FF0202081EE0E9495FF0DCFF02020812E4E94514FF02020807E0E94955C99703970303FF02020812E4E94514FF02020807E0E94955C99703970303"


def test_se_string_with_inner_str():
    bytes_ = b"\x02\x08\x9e\xe4\xe9E\x14\xff\x96\x02\x08\x92\xe0\xe9I7\xff\x8a\x02\x10\x01\x03\x02H\x04\xf2\x01\xf8\x03\x02I\x04\xf2\x01\xf9\x03Additional Effect: \x02I\x02\x01\x03\x02H\x02\x01\x03Grants \x02H\x04\xf2\x01\xfa\x03\x02I\x04\xf2\x01\xfb\x03Goring Blade Ready\x02I\x02\x01\x03\x02H\x02\x01\x03\x02\x10\x01\x03\x02H\x04\xf2\x01\xf8\x03\x02I\x04\xf2\x01\xf9\x03Duration: \x02I\x02\x01\x03\x02H\x02\x01\x0330s\xff\x01\x03\xff\x01\x03"
    se_string = SeString(bytes_)
    s = str(se_string)
    assert (
        s
        == """{macro("IF", [expression("Eq", expression("GlobalNumber", expression("U32", 68)), expression("U32", 19)),expression("SeString", [macro("IF", [expression("Ge", expression("GlobalNumber", expression("U32", 72)), expression("U32", 54)),expression("SeString", [macro("NEW_LINE", []),macro("COLOR_TYPE", [expression("U32Packed", 504)]),macro("EDGE_COLOR_TYPE", [expression("U32Packed", 505)]),b'Additional Effect: ',macro("EDGE_COLOR_TYPE", [expression("U32", 0)]),macro("COLOR_TYPE", [expression("U32", 0)]),b'Grants ',macro("COLOR_TYPE", [expression("U32Packed", 506)]),macro("EDGE_COLOR_TYPE", [expression("U32Packed", 507)]),b'Goring Blade Ready',macro("EDGE_COLOR_TYPE", [expression("U32", 0)]),macro("COLOR_TYPE", [expression("U32", 0)]),macro("NEW_LINE", []),macro("COLOR_TYPE", [expression("U32Packed", 504)]),macro("EDGE_COLOR_TYPE", [expression("U32Packed", 505)]),b'Duration: ',macro("EDGE_COLOR_TYPE", [expression("U32", 0)]),macro("COLOR_TYPE", [expression("U32", 0)]),b'30s']),expression("SeString", [])])]),expression("SeString", [])], to_hex=True)}"""
    )


def test_direct_evaluator_macro():
    hex_str = macro(
        "IF",
        [
            expression(
                "Eq",
                expression("GlobalNumber", expression("U32", 68)),
                expression("U32", 19),
            ),
            expression(
                "SeString",
                [
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
                                [
                                    macro(
                                        "IF",
                                        [
                                            expression(
                                                "Eq",
                                                expression(
                                                    "GlobalNumber",
                                                    expression("U32", 68),
                                                ),
                                                expression("U32", 19),
                                            ),
                                            expression(
                                                "SeString",
                                                [
                                                    macro(
                                                        "IF",
                                                        [
                                                            expression(
                                                                "Ge",
                                                                expression(
                                                                    "GlobalNumber",
                                                                    expression(
                                                                        "U32", 72
                                                                    ),
                                                                ),
                                                                expression("U32", 84),
                                                            ),
                                                            expression("U32", 200),
                                                            expression("U32", 150),
                                                        ],
                                                    )
                                                ],
                                            ),
                                            expression("U32", 150),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
            expression(
                "SeString",
                [
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
                                [
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
                                    )
                                ],
                            ),
                            expression("U32", 150),
                        ],
                    )
                ],
            ),
        ],
        to_hex=True,
    )

    assert (
        hex_str
        == "<hex:02083FE4E94514FF2202081EE0E9495FF0DCFF16020812E4E94514FF0B020807E0E94955C99703970303FF16020812E4E94514FF0B020807E0E94955C99703970303>"
    )


def test_direct_evaluator_inline_macro():
    hex_str = macro(
        "IF",
        [
            expression(
                "Eq",
                expression("GlobalNumber", expression("U32", 68)),
                expression("U32", 19),
            ),
            expression(
                "SeString",
                [
                    macro(
                        "IF",
                        [
                            expression(
                                "Ge",
                                expression("GlobalNumber", expression("U32", 72)),
                                expression("U32", 54),
                            ),
                            expression(
                                "SeString",
                                [
                                    macro("NEW_LINE", []),
                                    macro("COLOR_TYPE", [expression("U32Packed", 504)]),
                                    macro(
                                        "EDGE_COLOR_TYPE",
                                        [expression("U32Packed", 505)],
                                    ),
                                    b"Additional Effect: ",
                                    macro("EDGE_COLOR_TYPE", [expression("U32", 0)]),
                                    macro("COLOR_TYPE", [expression("U32", 0)]),
                                    b"Grants ",
                                    macro("COLOR_TYPE", [expression("U32Packed", 506)]),
                                    macro(
                                        "EDGE_COLOR_TYPE",
                                        [expression("U32Packed", 507)],
                                    ),
                                    b"Goring Blade Ready",
                                    macro("EDGE_COLOR_TYPE", [expression("U32", 0)]),
                                    macro("COLOR_TYPE", [expression("U32", 0)]),
                                    macro("NEW_LINE", []),
                                    macro("COLOR_TYPE", [expression("U32Packed", 504)]),
                                    macro(
                                        "EDGE_COLOR_TYPE",
                                        [expression("U32Packed", 505)],
                                    ),
                                    b"Duration: ",
                                    macro("EDGE_COLOR_TYPE", [expression("U32", 0)]),
                                    macro("COLOR_TYPE", [expression("U32", 0)]),
                                    b"30s",
                                ],
                            ),
                            expression("SeString", []),
                        ],
                    )
                ],
            ),
            expression("SeString", []),
        ],
        to_hex=True,
    )
    assert (
        hex_str
        == """<hex:02089EE4E94514FF96020892E0E94937FF8A02100103024804F201F803024904F201F9034164646974696F6E616C204566666563743A20024902010302480201034772616E747320024804F201FA03024904F201FB03476F72696E6720426C6164652052656164790249020103024802010302100103024804F201F803024904F201F9034475726174696F6E3A2002490201030248020103333073FF0103FF0103>"""
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
