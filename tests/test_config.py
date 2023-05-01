from pathlib import Path

import pytest

import ssort._config as config


def test_default_skip_defined():
    assert hasattr(config, "DEFAULT_SKIP")


class TestIterValidPythonFiles:
    @pytest.fixture()
    def names(self):
        return [
            "apple.py",
            "cat.py",
            "cats.py",
            "dir/bark.py",
            "dir/meow.py",
            "dog.py",
            "cats/not_a_cat.py",
        ]

    @pytest.fixture()
    def skip_glob(self):
        return ["dir/*", "cat*"]

    @pytest.fixture()
    def is_invalid_glob(self, tmp_path):
        def fun(path):
            return path.relative_to(tmp_path) in [
                Path("cat.py"),
                Path("cats.py"),
                Path("dir/bark.py"),
                Path("dir/meow.py"),
            ]

        return fun

    @pytest.fixture()
    def is_invalid(self, names):
        def fun(name):
            return name in names

        return fun

    @pytest.fixture()
    def folder(self, tmp_path, names):
        for name in names:
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return tmp_path

    @pytest.fixture()
    def files(self, names, folder):
        return [folder / name for name in names]

    def test_is_invalid_skip_only(self, names, folder, is_invalid, files):
        cfg = config.Config(skip=names)

        valid = folder / "banana.py"
        valid.touch()
        files.append(valid)

        valid = folder / "dir" / "banana.py"
        valid.touch()
        files.append(valid)

        for file in files:
            assert is_invalid(file.name) == cfg.is_invalid(file)

    def test_is_invalid_extend_skip_only(
        self, names, folder, is_invalid, files
    ):
        cfg = config.Config(skip=[], extend_skip=names)

        valid = folder / "banana.py"
        valid.touch()
        files.append(valid)

        valid = folder / "dir" / "banana.py"
        valid.touch()
        files.append(valid)

        for file in files:
            assert is_invalid(file.name) == cfg.is_invalid(file)

    def test_is_invalid_skip_glob_only(
        self, skip_glob, is_invalid_glob, files
    ):
        cfg = config.Config(skip=[], skip_glob=skip_glob)

        for file in files:
            assert is_invalid_glob(file) == cfg.is_invalid(file)

    def test_iter_valid_python_files_recursive(
        self, folder, is_invalid, names
    ):
        ret = list(
            config.iter_valid_python_files_recursive(
                folder, is_invalid=is_invalid
            )
        )

        assert len(ret) == len(names)

        for name in ret:
            assert str(name.relative_to(folder)) in names

    def test_iter_valid_python_files_recursive_empty(self, tmp_path):
        with pytest.raises(StopIteration):
            next(
                config.iter_valid_python_files_recursive(
                    tmp_path, is_invalid=lambda x: True
                )
            )


class TestConfig:
    def test___init___default_values(self):
        cfg = config.Config()

        assert hasattr(cfg, "skip")
        assert hasattr(cfg, "extend_skip")

        assert isinstance(cfg.skip, frozenset)
        assert len(cfg.skip) > 0

        assert cfg.extend_skip == []

    def test___init___overwrite_default(self):
        cfg = config.Config(skip="no", extend_skip="nono")

        assert cfg.skip == "no"
        assert cfg.extend_skip == "nono"

    def test_is_invalid(self):
        skip = ["hello", "banana"]
        extend_skip = ["world"]

        cfg = config.Config(skip=skip, extend_skip=extend_skip)

        skip.extend(extend_skip)

        for s in skip:
            assert cfg.is_invalid(Path(s))
            assert cfg.is_invalid(Path("directory") / s)
            assert not cfg.is_invalid(Path(s) / "directory")

        for s in ["apple", "bananas", "bananas/worlds", "Hello"]:
            assert not cfg.is_invalid(Path(s))

    @pytest.fixture()
    def mock_iter(self, mocker):
        return mocker.patch(
            "ssort._config.iter_valid_python_files_recursive",
            return_value=[None],
        )

    def test_iterate_files_matching_patterns_existing_python_file(
        self, tmp_path, mock_iter
    ):
        path = tmp_path / "file.py"
        path.touch()

        cfg = config.Config()
        ret = cfg.iterate_files_matching_patterns([path])

        assert list(ret) == [path]
        mock_iter.assert_not_called()

    def test_iterate_files_matching_patterns_missing_python_file(
        self, tmp_path, mock_iter
    ):
        path = tmp_path / "file.py"

        cfg = config.Config()
        ret = cfg.iterate_files_matching_patterns([path])

        assert list(ret) == []
        mock_iter.assert_not_called()

    def test_iterate_files_matching_patterns_dir(self, tmp_path, mock_iter):
        path0 = tmp_path / "dir0"
        path1 = tmp_path / "dir1"
        path0.mkdir()
        path1.mkdir()

        cfg = config.Config()
        ret = cfg.iterate_files_matching_patterns([path0, path1])

        assert list(ret) == [None, None]
        mock_iter.assert_any_call(path0, is_invalid=cfg.is_invalid)
        mock_iter.assert_any_call(path1, is_invalid=cfg.is_invalid)
        assert mock_iter.call_count == 2


@pytest.fixture()
def toml(tmp_path):
    toml = """
    [tool.ssort]
    banana = 'banana'
    extend_skip = ['extend_skip']
    skip = ['skip']
    name-with-dash = '---'

    [tool.ssort.class]
    sort_order = []
    name-with-dash = '---'
    """

    path = tmp_path / "test.tml"
    with open(path, "w") as fh:
        fh.write(toml)

    return path


def test_parse_pyproject_toml(toml, mocker):
    ret = config.parse_pyproject_toml(toml)

    assert ret["banana"] == "banana"
    assert ret["name-with-dash"] == "---"
    assert ret["skip"] == ["skip"]

    assert ret["class"]["name-with-dash"] == "---"
    assert ret["class"]["sort_order"] == []
    assert ret["extend_skip"] == ["extend_skip"]


def test_get_config_from_root_exists(mocker, tmp_path):
    return_value = {"skyscraper": "tall"}
    mock_parse = mocker.patch(
        "ssort._config.parse_pyproject_toml", return_value=return_value
    )
    mock_config = mocker.patch("ssort._config.Config")

    path = tmp_path / "pyproject.toml"
    path.touch()
    assert path.exists()

    config.get_config_from_root(path.parent)

    mock_parse.assert_called_once_with(path)
    mock_config.assert_called_once_with(**return_value)


def test_get_config_from_root_not_exists(mocker, tmp_path):
    mock_parse = mocker.patch("ssort._config.parse_pyproject_toml")
    mock_config = mocker.patch("ssort._config.Config")

    path = tmp_path / "pyproject.toml"
    assert not path.exists()

    config.get_config_from_root(path.parent)

    mock_parse.assert_not_called()
    mock_config.assert_called_once_with(**{})
