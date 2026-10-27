import ast
import sys

import pytest

from ssort._parsing import parse, split_class

type_parameter_syntax = pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason="type parameter syntax was introduced in python 3.12",
)


def _split_text(source):
    return [
        statement.text for statement in parse(source, filename="<unknown>")
    ]


def test_split_empty():
    statements = _split_text("")
    assert statements == []


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


def test_split_attribute_docstrings():
    statements = _split_text(
        '"Module documentation."\n'
        "value = 1\n"
        '# Documentation comment.\n"Value documentation."\n'
        '"Additional documentation."\n'
        "other = 2"
    )
    assert statements == [
        '"Module documentation."',
        "value = 1\n"
        '# Documentation comment.\n"Value documentation."\n'
        '"Additional documentation."',
        "other = 2",
    ]


@pytest.mark.parametrize("expression", ["42", 'b"bytes"', 'f"{value}"', "f()"])
def test_split_attribute_docstrings_stop_at_non_string(expression):
    statements = _split_text(
        f'value = 1\n"Value documentation."\n{expression}\n"Unrelated."'
    )
    assert statements == [
        'value = 1\n"Value documentation."',
        expression,
        '"Unrelated."',
    ]


def test_split_attribute_docstring_coordinates():
    statements = list(parse('other = 0; value = 1\n"Value documentation."'))
    statement = statements[1]
    assert statement.text == 'value = 1\n"Value documentation."'
    assert (statement.start_row, statement.start_col) == (0, 11)
    assert isinstance(statement.node, ast.Assign)
    assert (statement.node.lineno, statement.node.col_offset) == (1, 11)
    assert (statement.node.end_lineno, statement.node.end_col_offset) == (
        1,
        20,
    )


def test_split_function_def():
    statements = _split_text(
        "@something(2, kwarg=3)\n"
        "def decorated(arg, *args, kwarg, **kwargs):\n"
        "    pass"
    )
    assert statements == [
        "@something(2, kwarg=3)\n"
        "def decorated(arg, *args, kwarg, **kwargs):\n"
        "    pass"
    ]


def _split_class(source, index=-1):
    statements = list(parse(source))
    head, body = split_class(statements[index])
    return head, [child.text for child in body]


def test_split_class_simple():
    actual = _split_class("class A:\n    attr = 2")
    expected = "class A:", ["    attr = 2"]
    assert actual == expected


@pytest.mark.parametrize(
    "source",
    [
        'class A: value = 1; "Value documentation."; "Additional."; other = 2',
        'class A:\n    value = 1\n    "Value documentation."\n'
        '    "Additional."\n    other = 2',
    ],
)
def test_split_class_attribute_docstrings(source):
    actual = _split_class(source)
    expected = "class A:", [
        '    value = 1\n    "Value documentation."\n    "Additional."',
        "    other = 2",
    ]
    assert actual == expected


@pytest.mark.parametrize("expression", ["42", 'b"bytes"', 'f"{value}"', "f()"])
def test_split_class_attribute_docstrings_stop_at_non_string(expression):
    actual = _split_class(
        'class A:\n    value = 1\n    "Value documentation."\n'
        f'    {expression}\n    "Unrelated."'
    )
    expected = "class A:", [
        '    value = 1\n    "Value documentation."',
        f"    {expression}",
        '    "Unrelated."',
    ]
    assert actual == expected


def test_split_class_attribute_docstring_coordinates():
    statement = next(parse('\nclass A:\n    value = 1\n    "Documentation."'))
    _, body = split_class(statement)
    assert body[0].text == '    value = 1\n    "Documentation."'
    assert (body[0].start_row, body[0].start_col) == (2, 0)
    assert body[0].node is statement.node.body[0]
    assert (body[0].node.lineno, body[0].node.col_offset) == (3, 4)


def test_split_class_single_line():
    actual = _split_class("class A: attr = 3")
    expected = "class A:", ["    attr = 3"]
    assert actual == expected


def test_split_class_single_line_multiple_statements():
    actual = _split_class("class A: a = 2; b = 3")
    expected = "class A:", ["    a = 2", "    b = 3"]
    assert actual == expected


def test_split_class_single_line_body_multiple_statements():
    actual = _split_class("class A:\n   a = 2; b = 3")
    expected = "class A:", ["   a = 2", "   b = 3"]
    assert actual == expected


def test_split_class_header_comment():
    actual = _split_class("class A:  # Something witty.\n    a = 1")
    expected = "class A:  # Something witty.", ["    a = 1"]
    assert actual == expected


def test_split_class_decorators():
    actual = _split_class("@decorator()\nclass A:\n    key: int")
    expected = "@decorator()\nclass A:", ["    key: int"]
    assert actual == expected


def test_split_class_decorator_single_line():
    actual = _split_class("@decorator()\nclass A: key: int")
    expected = "@decorator()\nclass A:", ["    key: int"]
    assert actual == expected


def test_split_class_leading_comment():
    actual = _split_class("# Comment.\nclass A:\n    pass")
    expected = "# Comment.\nclass A:", ["    pass"]
    assert actual == expected


def test_split_class_leading_comment_single_line():
    actual = _split_class("# Comment.\nclass A: pass")
    expected = "# Comment.\nclass A:", ["    pass"]
    assert actual == expected


def test_split_class_multiple():
    actual = _split_class("def a():\n    pass\n\nclass A:\n    pass")
    expected = "\nclass A:", ["    pass"]
    assert actual == expected


def test_split_class_with_bases():
    actual = _split_class("class A(\n    B,\n): pass")
    expected = "class A(\n    B,\n):", ["    pass"]
    assert actual == expected


@type_parameter_syntax
def test_split_class_with_type_params():
    actual = _split_class("class A[\n    B,\n]: pass")
    expected = "class A[\n    B,\n]:", ["    pass"]
    assert actual == expected
