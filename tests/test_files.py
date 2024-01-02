from pathlib import Path

import pytest

from ssort._files import current_working_dir, find_project_root


def test_current_working_dir():
    assert current_working_dir() == Path(".").resolve()


class TestFindProjectRoot:
    @pytest.fixture(
        params=[
            (".",),
            (".", "dir"),
            ("dir", "dirA/B"),
            ("dirA/B", "dir"),
            ("a/a/a", "b/b/b"),
            ("dir/a", "dir/b"),
        ]
    )
    def subdir(self, request):
        return request.param

    @pytest.fixture()
    def mock_current_working_dir(self, mocker, tmp_path):
        return mocker.patch(
            "ssort._files.current_working_dir", return_value=tmp_path / "root"
        )

    @pytest.fixture()
    def git(self, tmp_path):
        root = tmp_path / "root"
        (root / ".git").mkdir(parents=True)
        return root

    def test_find_project_root_git(
        self, subdir, git, mock_current_working_dir
    ):
        print(subdir)
        patterns = [git / sub for sub in subdir]

        for p in patterns:
            p.mkdir(parents=True, exist_ok=True)

        assert git == find_project_root(patterns)
        mock_current_working_dir.assert_called_once()

    @pytest.fixture()
    def pyproject(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        (root / "pyproject.toml").touch()
        return root

    def test_find_project_root_pyproject(
        self, subdir, pyproject, mock_current_working_dir
    ):
        patterns = [pyproject / sub for sub in subdir]

        for p in patterns:
            p.mkdir(parents=True, exist_ok=True)

        assert pyproject == find_project_root(patterns)
        mock_current_working_dir.assert_called_once()

    @pytest.fixture()
    def neither(self, tmp_path):
        root = tmp_path / "root"
        root.mkdir()
        return root

    def test_find_project_root_neither(
        self, subdir, neither, mocker, tmp_path
    ):
        mocker.patch(
            "ssort._files.current_working_dir",
            return_value=tmp_path / "root" / "dir",
        )
        patterns = [neither / sub for sub in subdir]

        if all(s.startswith("dir/") for s in subdir):
            neither = neither / "dir"

        for p in patterns:
            p.mkdir(parents=True, exist_ok=True)

        assert neither == find_project_root(patterns)
