class UnknownEncodingError(Exception):
    def __init__(self, msg, *, encoding):
        super().__init__(msg)
        self.encoding = encoding


class DecodingError(Exception):
    pass


class ParseError(Exception):
    def __init__(self, msg, *, lineno, col_offset):
        super().__init__(msg)
        self.lineno = lineno
        self.col_offset = col_offset
