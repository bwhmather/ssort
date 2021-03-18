import ast
import textwrap

from ssort._bindings import get_bindings


def _parse(source):
    source = textwrap.dedent(source)
    root = ast.parse(source)
    assert len(root.body) == 1
    node = root.body[0]
    print(ast.dump(node, include_attributes=True, indent=2))
    return node


def test_name_bindings():
    node = _parse("a")
    assert get_bindings(node) == []


def test_assignment_bindings():
    node = _parse("a = b")
    assert get_bindings(node) == ["a"]


def test_assignment_bindings_star():
    node = _parse("a, *b = c")
    assert get_bindings(node) == ["a", "b"]


def test_import_bindings():
    node = _parse("import something")
    assert get_bindings(node) == ["something"]


def test_import_bindings_from():
    node = _parse("from module import a, b")
    assert get_bindings(node) == ["a", "b"]


def test_import_bindings_as():
    node = _parse("import something as something_else")
    assert get_bindings(node) == ["something_else"]


def test_import_bindings_from_as():
    node = _parse("from module import something as something_else")
    assert get_bindings(node) == ["something_else"]
