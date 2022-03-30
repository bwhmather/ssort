from ssort._parsing import parse, split_class


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


def test_split_class_leading_comment():
    actual = _split_class("# Comment.\nclass A:\n    pass")
    expected = "# Comment.\nclass A:", ["    pass"]
    assert actual == expected


def test_split_class_multiple():
    actual = _split_class("def a():\n    pass\n\nclass A:\n    pass")
    expected = "\nclass A:", ["    pass"]
    assert actual == expected
