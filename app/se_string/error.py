class SeStringError(Exception):
    """Base class for errors in SeString logic."""

    pass


class UnexpectedEOFError(SeStringError):
    """End of source data was reached unexpectedly."""

    def __init__(self):
        super().__init__("Unexpected EOF")


class InvalidTextError(SeStringError):
    """An invalid text payload was read. Typically caused by invalid UTF-8."""

    def __init__(self):
        super().__init__("Invalid text payload")


class InvalidMacroError(SeStringError):
    """An invalid macro payload was read."""

    def __init__(self):
        super().__init__("Invalid macro payload")


class InvalidExpressionError(SeStringError):
    """An invalid expression was read."""

    def __init__(self):
        super().__init__("Invalid expression")


class InsufficientArgumentsError(SeStringError):
    """Insufficient expressions were provided as arguments to a macro call."""

    def __init__(self):
        super().__init__("Insufficient arguments for macro")


class TooManyArgumentsError(SeStringError):
    """Too many expressions were provided as arguments to a macro call."""

    def __init__(self):
        super().__init__("Too many arguments for macro")
