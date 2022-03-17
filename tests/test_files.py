from __future__ import annotations

import pathlib

import pytest

from ssort._files import is_ignored


def test_ignore_git(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("ignored")

    assert not is_ignored("src")
    assert not is_ignored("src/main.py")

    assert is_ignored("ignored")
    assert is_ignored("ignored/main.py")

    assert is_ignored("src/ignored")
    assert is_ignored("src/ignored/main.py")

    assert not is_ignored("../ignored")
    assert not is_ignored("../ignored/main.py")

    assert is_ignored(f"../{tmp_path.name}/ignored")
    assert is_ignored(f"../{tmp_path.name}/ignored/main.py")


def test_ignore_git_with_no_repo(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".gitignore").write_text("ignored")

    assert not is_ignored("src")
    assert not is_ignored("src/main.py")

    assert is_ignored("ignored")
    assert is_ignored("ignored/main.py")

    assert is_ignored("src/ignored")
    assert is_ignored("src/ignored/main.py")

    assert not is_ignored("../ignored")
    assert not is_ignored("../ignored/main.py")

    assert is_ignored(f"../{tmp_path.name}/ignored")
    assert is_ignored(f"../{tmp_path.name}/ignored/main.py")


def test_ignore_git_in_subdirectory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("parent")

    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / ".gitignore").write_text("child")

    assert not is_ignored("src")
    assert not is_ignored("src/main.py")
    assert not is_ignored("sub/src")
    assert not is_ignored("sub/src/main.py")

    assert is_ignored("parent")
    assert is_ignored("parent/main.py")
    assert is_ignored("sub/parent")
    assert is_ignored("sub/parent/main.py")

    assert is_ignored("src/parent")
    assert is_ignored("src/parent/main.py")
    assert is_ignored("sub/src/parent")
    assert is_ignored("sub/src/parent/main.py")

    assert not is_ignored("../parent")
    assert not is_ignored("../parent/main.py")
    assert not is_ignored("../sub/parent")
    assert not is_ignored("../sub/parent/main.py")

    assert is_ignored(f"../{tmp_path.name}/parent")
    assert is_ignored(f"../{tmp_path.name}/parent/main.py")
    assert is_ignored(f"../{tmp_path.name}/sub/parent")
    assert is_ignored(f"../{tmp_path.name}/sub/parent/main.py")

    assert not is_ignored("child")
    assert not is_ignored("child/main.py")
    assert is_ignored("sub/child")
    assert is_ignored("sub/child/main.py")

    assert not is_ignored("src/child")
    assert not is_ignored("src/child/main.py")
    assert is_ignored("sub/src/child")
    assert is_ignored("sub/src/child/main.py")

    assert not is_ignored("sub/../child")
    assert not is_ignored("sub/../child/main.py")

    assert is_ignored(f"../{tmp_path.name}/sub/child")
    assert is_ignored(f"../{tmp_path.name}/sub/child/main.py")


def test_ignore_git_in_working_subdirectory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("ignored")

    (tmp_path / "sub").mkdir()
    monkeypatch.chdir(tmp_path / "sub")

    assert not is_ignored("src")
    assert not is_ignored("src/main.py")

    assert is_ignored("ignored")
    assert is_ignored("ignored/main.py")

    assert is_ignored("src/ignored")
    assert is_ignored("src/ignored/main.py")

    assert is_ignored("../ignored")
    assert is_ignored("../ignored/main.py")

    assert is_ignored("../sub/ignored")
    assert is_ignored("../sub/ignored/main.py")

    assert not is_ignored("../../ignored")
    assert not is_ignored("../../ignored/main.py")


def test_ignore_git_in_working_parent_directory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / ".git").mkdir()
    (tmp_path / "sub" / ".gitignore").write_text("ignored")

    assert not is_ignored("ignored")
    assert not is_ignored("ignored/main.py")

    assert is_ignored("sub/ignored")
    assert is_ignored("sub/ignored/main.py")

    assert is_ignored("sub/src/ignored")
    assert is_ignored("sub/src/ignored/main.py")

    assert not is_ignored("sub/../ignored")
    assert not is_ignored("sub/../ignored/main.py")


def test_ignore_git_subdirectory_pattern(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("sub/ignored")

    (tmp_path / "sub").mkdir()

    assert not is_ignored("sub")
    assert not is_ignored("sub/main.py")

    assert is_ignored("sub/ignored")
    assert is_ignored("sub/ignored/main.py")


def test_ignore_git_symlink_recursive(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("ignored")

    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "link").symlink_to(tmp_path / "dir")

    assert not is_ignored("dir")
    assert not is_ignored("dir/link")
    assert not is_ignored("dir/link/link")

    assert is_ignored("dir/ignored")
    assert is_ignored("dir/link/ignored")
    assert is_ignored("dir/link/link/ignored")


def test_ignore_git_symlink_outside_repo(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "repo" / ".git").mkdir(parents=True)
    (tmp_path / "repo" / ".gitignore").write_text("link")

    (tmp_path / "link").mkdir()
    (tmp_path / "repo" / "link").symlink_to(tmp_path / "link")

    assert not is_ignored("link")
    assert not is_ignored("link/main.py")
    assert is_ignored("repo/link")
    assert is_ignored("repo/link/main.py")


def test_ignore_symlink_circular(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    (tmp_path / "link1").symlink_to(tmp_path / "link2")
    (tmp_path / "link2").symlink_to(tmp_path / "link1")

    assert not is_ignored("link1")
    assert not is_ignored("link2")
