from __future__ import annotations

import os
import pathlib
from typing import Iterable

import pathspec

from ssort._utils import memoize

_EMPTY_PATH_SPEC = pathspec.PathSpec([])


def _is_project_root(path: pathlib.Path) -> bool:
    if path == path.root or path == path.parent:
        return True

    if (path / ".git").is_dir():
        return True

    return False


def _get_ignore_patterns(path: pathlib.Path) -> pathspec.PathSpec:
    git_ignore = path / ".gitignore"
    if git_ignore.is_file():
        with git_ignore.open() as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)

    return _EMPTY_PATH_SPEC


@memoize
def _resolve_ignore_patterns(
    path: pathlib.Path,
) -> pathspec.PathSpec:
    if _is_project_root(path):
        return _get_ignore_patterns(path)

    return _resolve_ignore_patterns(path.parent) + _get_ignore_patterns(path)


def is_ignored(path: pathlib.Path) -> bool:
    try:
        path = path.resolve()
    except RuntimeError:
        return True

    ignore_patterns = _resolve_ignore_patterns(path)
    return ignore_patterns.match_file(path)


def find_python_files(
    patterns: Iterable[str | os.PathLike[str]],
) -> Iterable[pathlib.Path]:
    if not patterns:
        patterns = ["."]

    paths_set = set()
    paths_list = []
    for pattern in patterns:
        path = pathlib.Path(pattern)
        if path.suffix == ".py":
            subpaths = [path]
        else:
            subpaths = list(path.glob("**/*.py"))

        for subpath in sorted(subpaths):
            if subpath not in paths_set:
                paths_set.add(subpath)
                paths_list.append(subpath)

    return [path for path in paths_list if not is_ignored(path)]
