class ParserError(Exception):
    pass


class MissingRequiredColumnError(ParserError):
    pass


class InvalidWorkbookFormatError(ParserError):
    pass


class EmptyWorkbookError(ParserError):
    pass


class UnsupportedFileTypeError(ParserError):
    pass
