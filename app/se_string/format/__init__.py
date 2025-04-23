from app.config import settings
from app.se_string.cursor import SliceCursor
from app.se_string.expression import Expression
from app.se_string.macro_kind import MacroKind


def __format_if(payload):
    pass


def format_macro(payload):
    if settings.HEX_STR_MODE:
        content = "".join(f"{b:02X}" for b in payload.bytes) if payload.bytes else ""

        return (
            f"<hex:02{payload.kind.value:02X}{len(payload.bytes) + 1:02X}{content}03>"
        )

    arguments: SliceCursor = payload.args()

    match payload.kind:
        case MacroKind.IF:
            _arg_expr = Expression.read(arguments)

            return f"{{Macro_{payload.kind.name}({payload.bytes})}}"

        case _:
            # arg_expr = Expression.read(arguments)
            return f"{{Macro_{payload.kind.name}({payload.bytes})}}"
