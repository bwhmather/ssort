"""
The python source code statement sorter.
"""
from ssort._exceptions import ResolutionError
from ssort._ssort import ssort

# Let linting tools know that we mean to re-export ResolutionError.
assert ResolutionError is not None

__version__ = "0.9.2"
__all__ = ["ssort"]
