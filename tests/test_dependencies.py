import ast
import textwrap

from ssort._dependencies import get_dependencies


def _parse(source):
    source = textwrap.dedent(source)
    root = ast.parse(source)
    assert len(root.body) == 1
    node = root.body[0]
    print(ast.dump(node, include_attributes=True, indent=2))
    return node


def test_function_call_dependencies():
    node = _parse("function(1, arg_value, kwarg=kwarg_value, kwarg_2=2)")
    assert get_dependencies(node) == ["function", "arg_value", "kwarg_value"]


def test_function_call_dependencies_arg_unpacking():
    node = _parse("function(*args)")
    assert get_dependencies(node) == ["function", "args"]


def test_function_call_dependencies_kwarg_unpacking():
    node = _parse("function(*kwargs)")
    assert get_dependencies(node) == ["function", "kwargs"]


def test_method_call_dependencies():
    node = _parse("obj.method(arg_value, kwarg=kwarg_value)")
    assert get_dependencies(node) == ["obj", "arg_value", "kwarg_value"]


def test_decorator_dependencies():
    node = _parse(
        """
        @decorator(arg)
        def function():
            pass
        """
    )
    assert get_dependencies(node) == ["decorator", "arg"]


def test_name_dependencies():
    node = _parse("name")
    assert get_dependencies(node) == ["name"]


def test_assignment_dependencies():
    node = _parse("a = b")
    assert get_dependencies(node) == ["b"]


def test_function_dependencies():
    node = _parse(
        """
        def function():
            name
        """
    )
    assert get_dependencies(node) == ["name"]


def test_function_dependencies_multiple():
    node = _parse(
        """
        def function():
            a
            b
        """
    )
    assert get_dependencies(node) == ["a", "b"]


def test_function_dependencies_arg_shadows():
    node = _parse(
        """
        def function(arg):
            arg
        """
    )
    assert get_dependencies(node) == []


def test_function_dependencies_assignment_shadows():
    node = _parse(
        """
        def function():
            a = b
            a
        """
    )
    assert get_dependencies(node) == ["b"]


def test_function_dependencies_rest_shadows():
    node = _parse(
        """
        def function():
            _, *rest = value
            rest
        """
    )
    assert get_dependencies(node) == ["value"]


def test_function_dependencies_shadowed_after():
    node = _parse(
        """
        def function():
            a
            a = b
        """
    )
    assert get_dependencies(node) == ["b"]


def test_tuple_dependencies():
    node = _parse("(a, b, 3)")
    assert get_dependencies(node) == ["a", "b"]


def test_tuple_dependencies_star_unpacking():
    node = _parse("(a, *b)")
    assert get_dependencies(node) == ["a", "b"]
