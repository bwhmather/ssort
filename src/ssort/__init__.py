"""
The python source code statement sorter.
"""
from ssort._exceptions import ResolutionError, WildcardImportError
from ssort._ssort import ssort

# Let linting tools know that we do mean to re-export exception classes.
assert ResolutionError is not None
assert WildcardImportError is not None

__version__ = "0.11.1"
__all__ = ["ssort"]
