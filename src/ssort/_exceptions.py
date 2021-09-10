class ResolutionError(Exception):
    def __init__(self, msg, *, unresolved):
        super().__init__(msg)
        self.unresolved = unresolved
