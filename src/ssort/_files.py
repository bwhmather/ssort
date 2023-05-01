from pathlib import Path


def find_project_root(patterns):
    all_patterns = [Path(".").resolve()]

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
