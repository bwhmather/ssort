import subprocess
import sys

import pytest

_good = b"""
def _private():
    pass

def public():
    return _private()
"""

_unsorted = b"""
def public():
    return _private()

def _private():
    pass
"""

_encoding = b"""
# coding=invalid-encoding
"""

_character = b"""
# coding=ascii
\xfe = 2
"""

_syntax = b"""
def _private(
    pass

def public(
    return _private()
"""

_resolution = b"""
def _private():
    pass

def public():
    return _other()
"""

_double_resolution = b"""
def _private():
    pass

def public():
    return _other() + _same()
"""


def _write_fixtures(dirpath, texts):
    paths = []
    for index, text in enumerate(texts):
        path = dirpath / f"file_{index:04}.py"
        path.write_bytes(text)
        paths.append(str(path))
    return paths


@pytest.fixture(params=["entrypoint", "module"])
def check(request):
    def _check(dirpath):
        ssort_exe = {
            "entrypoint": ["ssort"],
            "module": [sys.executable, "-m", "ssort"],
        }[request.param]

        result = subprocess.run(
            [*ssort_exe, "--check", str(dirpath)],
            capture_output=True,
            encoding="utf-8",
        )
        return result.stderr.splitlines(keepends=True), result.returncode

    return _check


@pytest.fixture(params=["entrypoint", "module"])
def ssort(request):
    def _ssort(dirpath):
        ssort_exe = {
            "entrypoint": ["ssort"],
            "module": [sys.executable, "-m", "ssort"],
        }[request.param]

        result = subprocess.run(
            [*ssort_exe, str(dirpath)],
            capture_output=True,
            encoding="utf-8",
        )
        return result.stderr.splitlines(keepends=True), result.returncode

    return _ssort


def test_check_all_well(check, tmp_path):
    _write_fixtures(tmp_path, [_good, _good, _good])
    expected_msgs = [
        "3 files would be left unchanged\n",
    ]
    expected_status = 0
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_one_unsorted(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _good, _good])
    expected_msgs = [
        f"ERROR: {paths[0]!r} is incorrectly sorted\n",
        "1 file would be resorted, 2 files would be left unchanged\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_all_unsorted(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _unsorted, _unsorted])
    expected_msgs = [
        f"ERROR: {paths[0]!r} is incorrectly sorted\n",
        f"ERROR: {paths[1]!r} is incorrectly sorted\n",
        f"ERROR: {paths[2]!r} is incorrectly sorted\n",
        "3 files would be resorted\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_one_syntax_error(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _good, _good])
    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_all_syntax_error(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _syntax, _syntax])
    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        f"ERROR: syntax error in {paths[1]!r}: line 3, column 5\n",
        f"ERROR: syntax error in {paths[2]!r}: line 3, column 5\n",
        "3 files would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_resolution_error(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_resolution, _good, _good])
    expected_msgs = [
        f"ERROR: unresolved dependency '_other' in {paths[0]!r}: line 6, column 11\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_double_resolution_error(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_double_resolution, _good, _good])
    expected_msgs = [
        f"ERROR: unresolved dependency '_other' in {paths[0]!r}: line 6, column 11\n",
        f"ERROR: unresolved dependency '_same' in {paths[0]!r}: line 6, column 22\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_one_unsorted_one_syntax_error(check, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _unsorted, _good])
    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        f"ERROR: {paths[1]!r} is incorrectly sorted\n",
        "1 file would be resorted, 1 file would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = check(tmp_path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_all_well(ssort, tmp_path):
    _write_fixtures(tmp_path, [_good, _good, _good])

    expected_msgs = [
        "3 files were left unchanged\n",
    ]
    expected_status = 0

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_one_unsorted(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _good, _good])

    expected_msgs = [
        f"Sorting {paths[0]!r}\n",
        "1 file was resorted, 2 files were left unchanged\n",
    ]
    expected_status = 0

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_all_unsorted(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _unsorted, _unsorted])

    expected_msgs = [
        f"Sorting {paths[0]!r}\n",
        f"Sorting {paths[1]!r}\n",
        f"Sorting {paths[2]!r}\n",
        "3 files were resorted\n",
    ]
    expected_status = 0

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_one_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _good, _good])

    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        "2 files were left unchanged, 1 file was not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_all_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _syntax, _syntax])

    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        f"ERROR: syntax error in {paths[1]!r}: line 3, column 5\n",
        f"ERROR: syntax error in {paths[2]!r}: line 3, column 5\n",
        "3 files were not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_resolution_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_resolution, _good, _good])

    expected_msgs = [
        f"ERROR: unresolved dependency '_other' in {paths[0]!r}: line 6, column 11\n",
        "2 files were left unchanged, 1 file was not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_one_unsorted_one_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _unsorted, _good])

    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        f"Sorting {paths[1]!r}\n",
        "1 file was resorted, 1 file was left unchanged, 1 file was not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_encoding_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_encoding])

    expected_msgs = [
        f"ERROR: unknown encoding, 'invalid-encoding', in {paths[0]!r}\n",
        "1 file was not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_character_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_character])

    expected_msgs = [
        f"ERROR: encoding error in {paths[0]!r}: 'ascii' codec can't decode byte 0xfe in position 16: ordinal not in range(128)\n",
        "1 file was not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_empty_dir(ssort, tmp_path):
    expected_msgs = ["No files are present to be sorted. Nothing to do.\n"]
    expected_status = 0

    actual_msgs, actual_status = ssort(tmp_path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_non_existent_file(ssort, tmp_path):
    path = tmp_path / "file.py"

    expected_msgs = [
        f"ERROR: '{path}' does not exist\n",
        "1 file was not sortable\n",
    ]
    expected_status = 1

    actual_msgs, actual_status = ssort(path)

    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_no_py_extension(ssort, tmp_path):
    path = tmp_path / "file"
    path.write_bytes(_good)
    expected_msgs = ["1 file was left unchanged\n"]
    expected_status = 0
    actual_msgs, actual_status = ssort(path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_unreadable_file(ssort, tmp_path):
    path = tmp_path / "file.py"
    path.write_bytes(_good)
    path.chmod(0)
    expected_msgs = [
        f"ERROR: '{path}' is not readable\n",
        "1 file was not sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = ssort(path)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_ssort_run_module():
    entrypoint_result = subprocess.run(
        ["ssort", "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    entrypoint_output = entrypoint_result.stderr.splitlines(keepends=True)

    module_result = subprocess.run(
        [sys.executable, "-m", "ssort", "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    module_output = module_result.stderr.splitlines(keepends=True)

    assert module_output == entrypoint_output
