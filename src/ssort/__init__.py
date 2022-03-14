"""
The python source code statement sorter.
"""
from ssort._exceptions import (
    DecodingError,
    ResolutionError,
    UnknownEncodingError,
    WildcardImportError,
)
from ssort._ssort import ssort

# Let linting tools know that we do mean to re-export exception classes.
assert DecodingError is not None
assert ResolutionError is not None
assert UnknownEncodingError is not None
assert WildcardImportError is not None

__version__ = "0.11.2"
__all__ = ["ssort"]
