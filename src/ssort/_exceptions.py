class UnknownEncodingError(Exception):
    def __init__(self, msg, *, encoding):
        super().__init__(msg)
        self.encoding = encoding


class DecodingError(Exception):
    pass


class ResolutionError(Exception):
    def __init__(self, msg, *, unresolved):
        super().__init__(msg)
        self.unresolved = unresolved


class WildcardImportError(Exception):
    pass
