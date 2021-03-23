import io

from ssort._parsing import split


def _split_text(source):
    f = io.StringIO(source)
    return [text for text, ast in split(f, "<unknown>")]


def test_split_assignment():
    statements = _split_text("a = 4")
    assert statements == ["a = 4"]


def test_split_assignment_trailing_newline():
    statements = _split_text("a = 4\n")
    assert statements == ["a = 4"]


def test_split_assignment_leading_newlines():
    statements = _split_text("\n\na = 4")
    assert statements == ["\n\na = 4"]


def test_split_assignments():
    statements = _split_text("a = 4\nb = 2")
    assert statements == ["a = 4", "b = 2"]


def test_split_assignments_same_line():
    statements = _split_text("a = 4; b = 2")
    assert statements == ["a = 4", "b = 2"]


def test_split_assignments_same_line_whitespace_before_semicolon():
    statements = _split_text("a = 4 ;b = 2")
    assert statements == ["a = 4", "b = 2"]


def test_split_assignments_trailing_comment():
    statements = _split_text("a = 4  # Assign a\nb = 2  # Assign b")
    assert statements == ["a = 4  # Assign a", "b = 2  # Assign b"]


def test_split_assignments_leading_comment():
    statements = _split_text("# Assign a\na = 4\n# Assign b\nb = 2")
    assert statements == ["# Assign a\na = 4", "# Assign b\nb = 2"]


def test_split_assignments_leading_and_trailing_comments():
    statements = _split_text(
        "# Before a\na = 4  # After a\n# Before b\nb = 2  # After b"
    )
    assert statements == [
        "# Before a\na = 4  # After a",
        "# Before b\nb = 2  # After b",
    ]
