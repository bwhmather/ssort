import pytest

from ssort._files import find_project_root

subdirs = [
    (".",),
    (".", "dir"),
    ("dir", "dirA/B"),
    ("dirA/B", "dir"),
    ("a/a/a", "b/b/b"),
    ("dir/a", "dir/b"),
]


@pytest.fixture()
def git(tmp_path):
    root = tmp_path / "root"
    (root / ".git").mkdir(parents=True)
    return root


@pytest.mark.parametrize("subdir", subdirs)
def test_find_project_root_git(subdir, git):
    print(subdir)
    patterns = [git / sub for sub in subdir]

    for p in patterns:
        p.mkdir(parents=True, exist_ok=True)

    assert git == find_project_root(patterns)


@pytest.fixture()
def pyproject(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "pyproject.toml").touch()
    return root


@pytest.mark.parametrize("subdir", subdirs)
def test_find_project_root_pyproject(subdir, pyproject):
    patterns = [pyproject / sub for sub in subdir]

    for p in patterns:
        p.mkdir(parents=True, exist_ok=True)

    assert pyproject == find_project_root(patterns)


@pytest.fixture()
def neither(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    return root


@pytest.mark.parametrize("subdir", subdirs)
def test_find_project_root_neither(subdir, neither):
    patterns = [neither / sub for sub in subdir]

    if all(s.startswith("dir/") for s in subdir):
        neither = neither / "dir"

    for p in patterns:
        p.mkdir(parents=True, exist_ok=True)

    assert neither == find_project_root(patterns)
