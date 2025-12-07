import os
import pathlib
import subprocess
import sys

import pytest

from ssort import __version__
from ssort._utils import escape_path

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


def _read_fixtures(paths):
    return [pathlib.Path(path).read_bytes() for path in paths]


def _messages(stderr):
    return stderr.decode("utf-8").splitlines(keepends=True)


@pytest.fixture(params=["entrypoint", "module"])
def ssort(request):
    def _ssort(*args, input=""):
        ssort_exe = {
            "entrypoint": ["ssort"],
            "module": [sys.executable, "-m", "ssort"],
        }[request.param]

        result = subprocess.run(
            [*ssort_exe, *args],
            capture_output=True,
            input=input,
            env={**os.environ, "COLUMNS": "80"},
        )
        return result.stdout, result.stderr, result.returncode

    return _ssort


def test_check_all_well(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_good, _good, _good])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        "3 files would be left unchanged\n",
    ]
    assert status == 0
    assert _read_fixtures(paths) == [_good, _good, _good]


def test_check_one_unsorted(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _good, _good])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: {escape_path(paths[0])} is incorrectly sorted\n",
        "1 file would be resorted, 2 files would be left unchanged\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_unsorted, _good, _good]


def test_check_all_unsorted(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _unsorted, _unsorted])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: {escape_path(paths[0])} is incorrectly sorted\n",
        f"ERROR: {escape_path(paths[1])} is incorrectly sorted\n",
        f"ERROR: {escape_path(paths[2])} is incorrectly sorted\n",
        "3 files would be resorted\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_unsorted, _unsorted, _unsorted]


def test_check_one_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _good, _good])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: syntax error in {escape_path(paths[0])}: line 3, column 5\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_syntax, _good, _good]


def test_check_all_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _syntax, _syntax])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: syntax error in {escape_path(paths[0])}: line 3, column 5\n",
        f"ERROR: syntax error in {escape_path(paths[1])}: line 3, column 5\n",
        f"ERROR: syntax error in {escape_path(paths[2])}: line 3, column 5\n",
        "3 files would not be sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_syntax, _syntax, _syntax]


def test_check_resolution_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_resolution, _good, _good])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: unresolved dependency '_other' in {escape_path(paths[0])}: line 6, column 11\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_resolution, _good, _good]


def test_check_double_resolution_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_double_resolution, _good, _good])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: unresolved dependency '_other' in {escape_path(paths[0])}: line 6, column 11\n",
        f"ERROR: unresolved dependency '_same' in {escape_path(paths[0])}: line 6, column 22\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_double_resolution, _good, _good]


def test_check_one_unsorted_one_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _unsorted, _good])

    stdout, stderr, status = ssort("--check", tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: syntax error in {escape_path(paths[0])}: line 3, column 5\n",
        f"ERROR: {escape_path(paths[1])} is incorrectly sorted\n",
        "1 file would be resorted, 1 file would be left unchanged, 1 file would not be sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_syntax, _unsorted, _good]


def test_ssort_all_well(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_good, _good, _good])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        "3 files were left unchanged\n",
    ]
    assert status == 0
    assert _read_fixtures(paths) == [_good, _good, _good]


def test_ssort_one_unsorted(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _good, _good])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"Sorting {escape_path(paths[0])}\n",
        "1 file was resorted, 2 files were left unchanged\n",
    ]
    assert status == 0
    assert _read_fixtures(paths) == [_good, _good, _good]


def test_ssort_all_unsorted(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_unsorted, _unsorted, _unsorted])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"Sorting {escape_path(paths[0])}\n",
        f"Sorting {escape_path(paths[1])}\n",
        f"Sorting {escape_path(paths[2])}\n",
        "3 files were resorted\n",
    ]
    assert status == 0
    assert _read_fixtures(paths) == [_good, _good, _good]


def test_ssort_one_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _good, _good])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: syntax error in {escape_path(paths[0])}: line 3, column 5\n",
        "2 files were left unchanged, 1 file was not sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_syntax, _good, _good]


def test_ssort_all_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _syntax, _syntax])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: syntax error in {escape_path(paths[0])}: line 3, column 5\n",
        f"ERROR: syntax error in {escape_path(paths[1])}: line 3, column 5\n",
        f"ERROR: syntax error in {escape_path(paths[2])}: line 3, column 5\n",
        "3 files were not sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_syntax, _syntax, _syntax]


def test_ssort_resolution_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_resolution, _good, _good])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: unresolved dependency '_other' in {escape_path(paths[0])}: line 6, column 11\n",
        "2 files were left unchanged, 1 file was not sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_resolution, _good, _good]


def test_ssort_one_unsorted_one_syntax_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_syntax, _unsorted, _good])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: syntax error in {escape_path(paths[0])}: line 3, column 5\n",
        f"Sorting {escape_path(paths[1])}\n",
        "1 file was resorted, 1 file was left unchanged, 1 file was not sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_syntax, _good, _good]


def test_ssort_encoding_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_encoding])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: unknown encoding, 'invalid-encoding', in {escape_path(paths[0])}\n",
        "1 file was not sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_encoding]


def test_ssort_character_error(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [_character])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: encoding error in {escape_path(paths[0])}: 'ascii' codec can't decode byte 0xfe in position 16: ordinal not in range(128)\n",
        "1 file was not sortable\n",
    ]
    assert status == 1
    assert _read_fixtures(paths) == [_character]


def test_ssort_preserve_crlf_endlines(ssort, tmp_path):
    paths = _write_fixtures(tmp_path, [b"a = b\r\nb = 4"])

    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"Sorting {escape_path(paths[0])}\n",
        "1 file was resorted\n",
    ]
    assert status == 0

    assert _read_fixtures(paths) == [b"b = 4\r\na = b\r\n"]


def test_ssort_empty_dir(ssort, tmp_path):
    stdout, stderr, status = ssort(tmp_path)

    assert stdout == b""
    assert _messages(stderr) == [
        "No files are present to be sorted. Nothing to do.\n"
    ]

    assert status == 0


def test_ssort_non_existent_file(ssort, tmp_path):
    path = tmp_path / "file.py"

    stdout, stderr, status = ssort(path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: {escape_path(path)} does not exist\n",
        "1 file was not sortable\n",
    ]
    assert status == 1


def test_ssort_no_py_extension(ssort, tmp_path):
    path = tmp_path / "file"
    path.write_bytes(_good)

    stdout, stderr, status = ssort(path)

    assert stdout == b""
    assert _messages(stderr) == ["1 file was left unchanged\n"]
    assert status == 0


@pytest.mark.skipif(
    sys.platform == "win32", reason="can't block read on windows"
)
def test_ssort_unreadable_file(ssort, tmp_path):
    path = tmp_path / "file.py"
    path.write_bytes(_good)
    path.chmod(0)

    stdout, stderr, status = ssort(path)

    assert stdout == b""
    assert _messages(stderr) == [
        f"ERROR: {escape_path(path)} is not readable\n",
        "1 file was not sortable\n",
    ]
    assert status == 1


def test_ssort_version(ssort):
    stdout, stderr, status = ssort("--version")
    assert stdout.decode("utf-8") == f"ssort {__version__}\n"
    assert stderr == b""
    assert status == 0


def test_ssort_help(ssort):
    stdout, stderr, status = ssort("--help")

    assert (
        stdout.decode("utf-8")
        == f"""
usage: ssort [-h] [--version] [--diff] [--check] [files ...]

Sort python statements into dependency order

positional arguments:
  files       One or more python files to sort, or '-' for stdin.

{"optional arguments" if sys.version_info < (3, 10) else "options"}:
  -h, --help  show this help message and exit
  --version   Outputs version information and then exit
  --diff      Prints a diff of all changes ssort would make to a file.
  --check     Check the file for unsorted statements. Returns 0 if nothing
              needs to be changed. Otherwise returns 1.
""".lstrip()
    )
    assert stderr == b""
    assert status == 0


@pytest.mark.parametrize(
    ("stdin", "expected_stdout"),
    (
        (_unsorted, _good),
        (_good, _good),
        (_encoding, _encoding),
        (_character, _character),
        (_syntax, _syntax),
        (_resolution, _resolution),
        (_double_resolution, _double_resolution),
    ),
    ids=(
        "unsorted",
        "good",
        "encoding",
        "character",
        "syntax",
        "resolution",
        "double_resolution",
    ),
)
def test_ssort_stdin(stdin, expected_stdout, ssort):
    stdout, stderr, status = ssort("-", input=stdin)
    assert stdout == expected_stdout
