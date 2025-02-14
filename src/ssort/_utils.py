from __future__ import annotations

import functools
import io
import re
import shlex
import sys
import tokenize
from typing import Any, Callable, Generic, TypeVar

from ssort._exceptions import UnknownEncodingError


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


def cached_method(function: Callable[[Any], _T]) -> Callable[[Any], _T]:
    cached_attribute_name = f"_{function.__name__}_cache"

    @functools.wraps(function)
    def wrapper(self) -> _T:
        try:
            return getattr(self, cached_attribute_name)
        except AttributeError:
            value = function(self)
            setattr(self, cached_attribute_name, value)
            return value

    return wrapper


def escape_path(path):
    """
    Takes a `pathlib.Path` object and returns a string representation that can
    be safely copied into the system shell.
    """
    if sys.platform == "win32":
        # TODO
        return str(path)
    else:
        return shlex.quote(str(path))


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


_NEWLINE_RE = re.compile("(\r\n)|(\r)|(\n)")


def detect_newline(text):
    """
    Detects the newline character used in a source file based on the first
    occurence of '\\n', '\\r' or '\\r\\n'.
    """
    match = re.search(_NEWLINE_RE, text)
    if match is None:
        return "\n"
    return match[0]


def normalize_newlines(text):
    """
    Replaces all occurrences of '\r' and '\\r\\n' with \n.
    """
    return re.sub(_NEWLINE_RE, "\n", text)
