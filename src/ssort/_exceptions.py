class ResolutionError(Exception):
    def __init__(self, msg, *, unresolved):
        super().__init__(msg)


class WildcardImportError(Exception):
    pass
