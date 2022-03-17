from __future__ import annotations

import pathlib

import pytest

from ssort._files import is_ignored


def _is_ignored(path: str) -> bool:
    return is_ignored(pathlib.Path(path))


def test_ignore_git(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("ignored")

    assert not _is_ignored("src")
    assert not _is_ignored("src/main.py")

    assert _is_ignored("ignored")
    assert _is_ignored("ignored/main.py")

    assert _is_ignored("src/ignored")
    assert _is_ignored("src/ignored/main.py")

    assert not _is_ignored("../ignored")
    assert not _is_ignored("../ignored/main.py")

    assert _is_ignored(f"../{tmp_path.name}/ignored")
    assert _is_ignored(f"../{tmp_path.name}/ignored/main.py")


def test_ignore_git_with_no_git_directory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".gitignore").write_text("ignored")

    assert not _is_ignored("src")
    assert not _is_ignored("src/main.py")

    assert _is_ignored("ignored")
    assert _is_ignored("ignored/main.py")

    assert _is_ignored("src/ignored")
    assert _is_ignored("src/ignored/main.py")

    assert not _is_ignored("../ignored")
    assert not _is_ignored("../ignored/main.py")

    assert _is_ignored(f"../{tmp_path.name}/ignored")
    assert _is_ignored(f"../{tmp_path.name}/ignored/main.py")


def test_ignore_git_in_subdirectory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("parent")

    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / ".gitignore").write_text("child")

    assert not _is_ignored("src")
    assert not _is_ignored("src/main.py")
    assert not _is_ignored("sub/src")
    assert not _is_ignored("sub/src/main.py")

    assert _is_ignored("parent")
    assert _is_ignored("parent/main.py")
    assert _is_ignored("sub/parent")
    assert _is_ignored("sub/parent/main.py")

    assert _is_ignored("src/parent")
    assert _is_ignored("src/parent/main.py")
    assert _is_ignored("sub/src/parent")
    assert _is_ignored("sub/src/parent/main.py")

    assert not _is_ignored("../parent")
    assert not _is_ignored("../parent/main.py")
    assert not _is_ignored("../sub/parent")
    assert not _is_ignored("../sub/parent/main.py")

    assert _is_ignored(f"../{tmp_path.name}/parent")
    assert _is_ignored(f"../{tmp_path.name}/parent/main.py")
    assert _is_ignored(f"../{tmp_path.name}/sub/parent")
    assert _is_ignored(f"../{tmp_path.name}/sub/parent/main.py")

    assert not _is_ignored("child")
    assert not _is_ignored("child/main.py")
    assert _is_ignored("sub/child")
    assert _is_ignored("sub/child/main.py")

    assert not _is_ignored("src/child")
    assert not _is_ignored("src/child/main.py")
    assert _is_ignored("sub/src/child")
    assert _is_ignored("sub/src/child/main.py")

    assert not _is_ignored("sub/../child")
    assert not _is_ignored("sub/../child/main.py")

    assert _is_ignored(f"../{tmp_path.name}/sub/child")
    assert _is_ignored(f"../{tmp_path.name}/sub/child/main.py")


def test_ignore_git_in_working_subdirectory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("ignored")

    (tmp_path / "sub").mkdir()
    monkeypatch.chdir(tmp_path / "sub")

    assert not _is_ignored("src")
    assert not _is_ignored("src/main.py")

    assert _is_ignored("ignored")
    assert _is_ignored("ignored/main.py")

    assert _is_ignored("src/ignored")
    assert _is_ignored("src/ignored/main.py")

    assert _is_ignored("../ignored")
    assert _is_ignored("../ignored/main.py")

    assert _is_ignored("../sub/ignored")
    assert _is_ignored("../sub/ignored/main.py")

    assert not _is_ignored("../../ignored")
    assert not _is_ignored("../../ignored/main.py")


def test_ignore_git_in_working_parent_directory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / ".git").mkdir()
    (tmp_path / "sub" / ".gitignore").write_text("ignored")

    assert not _is_ignored("ignored")
    assert not _is_ignored("ignored/main.py")

    assert _is_ignored("sub/ignored")
    assert _is_ignored("sub/ignored/main.py")

    assert _is_ignored("sub/src/ignored")
    assert _is_ignored("sub/src/ignored/main.py")

    assert not _is_ignored("sub/../ignored")
    assert not _is_ignored("sub/../ignored/main.py")


def test_ignore_symlink_recursive(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "link").symlink_to(tmp_path / "dir")

    # Just make sure recursive symlinks don't cause unbounded recursion.
    assert not _is_ignored("dir")
    assert not _is_ignored("dir/link")
    assert not _is_ignored("dir/link/link")


def test_ignore_symlink_circular(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "link1").symlink_to(tmp_path / "link2")
    (tmp_path / "link2").symlink_to(tmp_path / "link1")

    # Unresolvable links should be ignored.
    assert _is_ignored("link1")
    assert _is_ignored("link2")
