class UnknownEncodingError(Exception):
    def __init__(self, msg, *, encoding):
        super().__init__(msg)
        self.encoding = encoding


class ResolutionError(Exception):
    def __init__(self, msg, *, unresolved):
        super().__init__(msg)


class WildcardImportError(Exception):
    pass
