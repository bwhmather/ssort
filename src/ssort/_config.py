from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    from tomllib import load
else:
    from tomli import load


DEFAULT_SKIP = frozenset(
    {
        ".bzr",
        ".direnv",
        ".eggs",
        ".git",
        ".hg",
        ".mypy_cache",
        ".nox",
        ".pants.d",
        ".pytype",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        "__pypackages__",
        "_build",
        "buck-out",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)


def iter_valid_python_files_recursive(folder, *, is_invalid):
    for child in folder.iterdir():
        if is_invalid(child):
            continue

        if child.is_file() and child.suffix == ".py":
            yield child

        if child.is_dir():
            yield from iter_valid_python_files_recursive(
                child, is_invalid=is_invalid
            )


@dataclass(frozen=True)
class Config:
    skip: frozenset | list = DEFAULT_SKIP
    extend_skip: list = field(default_factory=list)

    def iterate_files_matching_pattern(self, pattern):
        for pat in pattern:
            path = Path(pat).resolve()

            if path.is_file() and path.suffix == ".py":
                yield path
                continue

            if path.is_dir():
                invalid_names = set(self.skip) | set(self.extend_skip)
                yield from iter_valid_python_files_recursive(
                    path,
                    is_invalid=lambda x: x.name in invalid_names,
                )


def parse_pyproject_toml(path):
    with open(path, "rb") as fh:
        pyproject_toml = load(fh)

    config = pyproject_toml.get("tool", {}).get("ssort", {})
    config = {key.replace("-", "_"): val for key, val in config.items()}

    return config


def get_config_from_root(root):
    path_pyproject_toml = root / "pyproject.toml"

    if path_pyproject_toml.exists():
        config_dict = parse_pyproject_toml(path_pyproject_toml)
    else:
        config_dict = {}

    return Config(**config_dict)
