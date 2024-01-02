from __future__ import annotations

import io
import re
import shlex
import sys
import tokenize
from pathlib import Path

from ssort._exceptions import UnknownEncodingError

__all__ = [
    "detect_encoding",
    "detect_newline",
    "escape_path",
    "find_project_root",
    "normalize_newlines",
]


_NEWLINE_RE = re.compile("(\r\n)|(\r)|(\n)")


def current_working_dir():
    return Path(".").resolve()


def find_project_root(patterns):
    all_patterns = [current_working_dir()]

    if patterns:
        all_patterns.extend(patterns)

    paths = [Path(p).resolve() for p in all_patterns]
    parents_and_self = [
        list(reversed(p.parents)) + ([p] if p.is_dir() else []) for p in paths
    ]

    *_, (common_base, *_) = (
        common_parent
        for same_lvl_parent in zip(*parents_and_self)
        if len(common_parent := set(same_lvl_parent)) == 1
    )

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists() or (
            directory / "pyproject.toml"
        ).is_file():
            return directory

    return common_base


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
