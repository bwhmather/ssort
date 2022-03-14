from __future__ import annotations

import functools
import io
import re
import sys
import tokenize
from typing import Any, Callable, Generic, TypeVar

from ssort._exceptions import UnknownEncodingError

if sys.version_info < (3, 9):
    memoize = functools.lru_cache(maxsize=None)
else:
    memoize = functools.cache


def sort_key_from_iter(values):
    index = {statement: index for index, statement in enumerate(values)}
    key = lambda value: index[value]
    return key


_T = TypeVar("_T")


class _SingleDispatch(Generic[_T]):
    """A more performant implementation of functools.singledispatch."""

    def __init__(self, function: Callable[..., _T]) -> None:
        functools.update_wrapper(self, function)
        self._function: Callable[..., _T] = function
        self._functions: dict[type[Any], Callable[..., _T]] = {}

    def register(
        self, cls: type[Any]
    ) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
        def decorator(function: Callable[..., _T]) -> Callable[..., _T]:
            self._functions[cls] = function
            return function

        return decorator

    def __call__(self, arg: Any, *args: Any) -> _T:
        return self._functions.get(type(arg), self._function)(arg, *args)


single_dispatch = _SingleDispatch


def detect_encoding(bytestring):
    """
    Detect the encoding of a python source file based on "coding" comments, as
    defined in [PEP 263](https://www.python.org/dev/peps/pep-0263/).
    """
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(bytestring).readline)
    except SyntaxError as exc:
        raise UnknownEncodingError(
            exc.msg, encoding=re.match("unknown encoding: (.*)", exc.msg)[1]
        ) from exc
    return encoding
