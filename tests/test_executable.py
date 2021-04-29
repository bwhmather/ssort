import subprocess

_good = """
def _private():
    pass

def public():
    return _private()
"""

_unsorted = """
def public():
    return _private()

def _private():
    pass
"""

_syntax = """
def _private(
    pass

def public(
    return _private()
"""

_resolution = """
def _private():
    pass

def public():
    return _other()
"""


def _write_fixtures(dirpath, texts):
    paths = []
    for index, text in enumerate(texts):
        path = dirpath / f"file_{index:04}.py"
        path.write_text(text, encoding="utf-8")
        paths.append(str(path))
    return paths


def _check(dirpath):
    result = subprocess.run(
        ["ssort", "--check", str(dirpath)],
        capture_output=True,
        encoding="utf-8",
    )
    return result.stderr.splitlines(keepends=True), result.returncode


def test_check_all_well(tmpdir):
    _write_fixtures(tmpdir, [_good, _good, _good])
    expected_msgs = [
        "3 files would be left unchanged\n",
    ]
    expected_status = 0
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_one_unsorted(tmpdir):
    paths = _write_fixtures(tmpdir, [_unsorted, _good, _good])
    expected_msgs = [
        f"ERROR: {paths[0]!r} is incorrectly sorted\n",
        "1 file would be resorted, 2 files would be left unchanged\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_all_unsorted(tmpdir):
    paths = _write_fixtures(tmpdir, [_unsorted, _unsorted, _unsorted])
    expected_msgs = [
        f"ERROR: {paths[0]!r} is incorrectly sorted\n",
        f"ERROR: {paths[1]!r} is incorrectly sorted\n",
        f"ERROR: {paths[2]!r} is incorrectly sorted\n",
        "3 files would be resorted\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_one_syntax_error(tmpdir):
    paths = _write_fixtures(tmpdir, [_syntax, _good, _good])
    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_all_syntax_error(tmpdir):
    paths = _write_fixtures(tmpdir, [_syntax, _syntax, _syntax])
    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        f"ERROR: syntax error in {paths[1]!r}: line 3, column 5\n",
        f"ERROR: syntax error in {paths[2]!r}: line 3, column 5\n",
        "3 files would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_resolution_error(tmpdir):
    paths = _write_fixtures(tmpdir, [_resolution, _good, _good])
    expected_msgs = [
        f"ERROR: unresolved dependency '_other' in {paths[0]!r}: line 6, column 11\n",
        "2 files would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)


def test_check_one_unsorted_one_syntax_error(tmpdir):
    paths = _write_fixtures(tmpdir, [_syntax, _unsorted, _good])
    expected_msgs = [
        f"ERROR: syntax error in {paths[0]!r}: line 3, column 5\n",
        f"ERROR: {paths[1]!r} is incorrectly sorted\n",
        "1 file would be resorted, 1 file would be left unchanged, 1 file would not be sortable\n",
    ]
    expected_status = 1
    actual_msgs, actual_status = _check(tmpdir)
    assert (actual_msgs, actual_status) == (expected_msgs, expected_status)
