"""
The python source code statement sorter.
"""
from ssort._exceptions import ResolutionError
from ssort._ssort import ssort

# Let linting tools know that we mean to re-export ResolutionError.
assert ResolutionError is not None

__version__ = "0.10.1"
__all__ = ["ssort"]
