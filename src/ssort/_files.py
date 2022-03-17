from __future__ import annotations

import os
import pathlib
from typing import Iterable

import pathspec

from ssort._utils import memoize

_EMPTY_PATH_SPEC = pathspec.PathSpec([])


@memoize
def _is_project_root(path: pathlib.Path) -> bool:
    if path == path.root or path == path.parent:
        return True

    if (path / ".git").is_dir():
        return True

    return False


@memoize
def _get_ignore_patterns(path: pathlib.Path) -> pathspec.PathSpec:
    git_ignore = path / ".gitignore"
    if git_ignore.is_file():
        with git_ignore.open() as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)

    return _EMPTY_PATH_SPEC


def is_ignored(path: str | os.PathLike) -> bool:
    # Can't use pathlib.Path.resolve() here because we want to maintain
    # symbolic links.
    path = pathlib.Path(os.path.abspath(path))

    for part in (path, *path.parents):
        patterns = _get_ignore_patterns(part)
        if patterns.match_file(path.relative_to(part)):
            return True

        if _is_project_root(part):
            return False

    return False


def find_python_files(
    patterns: Iterable[str | os.PathLike[str]],
) -> Iterable[pathlib.Path]:
    if not patterns:
        patterns = ["."]

    paths_set = set()
    for pattern in patterns:
        path = pathlib.Path(pattern)
        if path.suffix == ".py":
            subpaths = [path]
        else:
            subpaths = [
                subpath
                for subpath in path.glob("**/*.py")
                if not is_ignored(subpath)
            ]

        for subpath in sorted(subpaths):
            if subpath not in paths_set:
                paths_set.add(subpath)
                yield subpath
