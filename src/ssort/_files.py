from pathlib import Path


def find_project_root(patterns):
    if not patterns:
        patterns = ["."]

    paths = [Path(p).resolve() for p in patterns]
    parents = [([p] if p.is_dir() else []) + list(p.parents) for p in paths]

    *_, (common_base, *_) = zip(*(reversed(p) for p in parents))

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists() or (
            directory / "pyproject.toml"
        ).is_file():
            return directory

    return directory
