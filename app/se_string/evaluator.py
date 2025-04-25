from itertools import chain

from app.se_string import ExpressionType, MacroKind
from app.se_string.packed import get_length_bytes, get_packed_u32_bytes


def expression(*args) -> list[int]:
    type = args[0]
    args = args[1:]
    match type:
        case ExpressionType.U32:
            value = args[0] + 1
            return [value]
        case ExpressionType.U32Packed:
            value = args[0]
            bytes_ = get_packed_u32_bytes(value)
            return list(bytes_)
        case ExpressionType.Millisecond:
            return [0xD8]
        case ExpressionType.Second:
            return [0xD9]
        case ExpressionType.Minute:
            return [0xDA]

        case ExpressionType.Hour:
            return [0xDB]
        case ExpressionType.Day:
            return [0xDC]
        case ExpressionType.Weekday:
            return [0xDD]
        case ExpressionType.Month:
            return [0xDE]
        case ExpressionType.Year:
            return [0xDF]
        case ExpressionType.Ge:
            condition_arg = args[0]
            condition_value = args[1]
            return [0xE0] + condition_arg + condition_value

        case ExpressionType.Gt:
            condition_arg = args[0]
            condition_value = args[1]
            return [0xE0] + condition_arg + condition_value
        case ExpressionType.Le:
            condition_arg = args[0]
            condition_value = args[1]
            return [0xE1] + condition_arg + condition_value

        case ExpressionType.Lt:
            condition_arg = args[0]
            condition_value = args[1]
            return [0xE2] + condition_arg + condition_value

        case ExpressionType.Eq:
            condition_arg = args[0]
            condition_value = args[1]
            return [0xE4] + condition_arg + condition_value

        case ExpressionType.Ne:
            condition_arg = args[0]
            condition_value = args[1]
            return [0xE5] + condition_arg + condition_value

        case ExpressionType.LocalNumber:
            value = args[0]

            return [0xE8] + value
        case ExpressionType.GlobalNumber:
            value = args[0]

            return [0xE9] + value
        case ExpressionType.LocalString:
            value = args[0]

            return [0xEA] + value

        case ExpressionType.GlobalString:
            value = args[0]
            return [0xEB] + value
        case ExpressionType.StackColor:
            return [0xEC]
        case ExpressionType.SeString:
            expression_byte = [0xFF]
            flat_list = list(chain.from_iterable(args[0]))
            ff_string_body = flat_list
            length_bytes = get_length_bytes(ff_string_body)

            return expression_byte + list(length_bytes) + ff_string_body
        case _:
            raise Exception("unknown type")
    return ""


def __flatten_recursive(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list) or isinstance(
            item, tuple
        ):  # Check if item is a list or tuple
            flat_list.extend(__flatten_recursive(item))  # Recursively flatten
        else:
            flat_list.append(item)
    return flat_list


def macro(*args, **kwargs):
    type = args[0]
    kind = MacroKind[type]
    args_value = args[1:]
    start_byte = [0x02]

    end_byte = [0x03]
    flat_list = list(chain.from_iterable(args_value[0]))
    length_bytes = get_length_bytes(flat_list)
    to_hex = kwargs.get("to_hex", False)

    macro_bytes = start_byte + [kind.value] + list(length_bytes) + flat_list + end_byte
    if to_hex:
        return f"<hex:{''.join(f'{b:02X}' for b in macro_bytes)}>"
    else:
        return macro_bytes


def evaluated_se_string(se_string: str):
    s = eval(f'f"""{se_string}"""')
    return s
