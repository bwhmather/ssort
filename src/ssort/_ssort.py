import ast

from ssort._bubble_sort import bubble_sort
from ssort._dependencies import statements_graph
from ssort._graphs import (
    is_topologically_sorted,
    replace_cycles,
    topological_sort,
)
from ssort._parsing import split, split_class
from ssort._statements import statement_node, statement_text
from ssort._utils import sort_key_from_iter

SPECIAL_PROPERTIES = [
    "__slots__",
]

LIFECYCLE_OPERATIONS = [
    # Lifecycle.
    "__new__",
    "__init__",
    "__del__",
    # Metaclasses.
    # TODO "__prepare__", ?
    "__init_subclass__",
    "__instancecheck__",
    "__subclasscheck__",
    # Generics.
    "__class_getitem__",
    # Descriptors.
    "__get__",
    "__set__",
    "__delete__",
    "__set_name__",
]

REGULAR_OPERATIONS = [
    # Callables.
    "__call__",
    # Attribute Access.
    "__getattr__",
    "__getattribute__",
    "__setattr__",
    "__delattr__",
    "__dir__",
    # Container Operations.
    "__len__",
    "__length_hint__",
    "__getitem__",
    "__setitem__",
    "__delitem__",
    "__missing__",
    "__iter__",
    "__reversed__",
    "__contains__",
    # Binary Operators.
    "__add__",
    "__radd__",
    "__iadd__",
    "__sub__",
    "__rsub__",
    "__isub__",
    "__mul__",
    "__rmul__",
    "__imul__",
    "__matmul__",
    "__rmatmul__",
    "__imatmul__",
    "__truediv__",
    "__rtruediv__",
    "__itruediv__",
    "__floordiv__",
    "__rfloordiv__",
    "__ifloordiv__",
    "__mod__",
    "__rmod__",
    "__imod__",
    "__divmod__",
    "__rdivmod__",
    "__pow__",
    "__rpow__",
    "__ipow__",
    "__lshift__",
    "__rlshift__",
    "__ilshift__",
    "__rshift__",
    "__rrshift__",
    "__irshift__",
    "__and__",
    "__rand__",
    "__iand__",
    "__xor__",
    "__rxor__",
    "__ixor__",
    "__or__",
    "__ror__",
    "__ior__",
    # Unary operators.
    "__neg__",
    "__pos__",
    "__abs__",
    "__invert__",
    # Rich comparison operators.
    "__lt__",
    "__le__",
    "__eq__",
    "__ne__",
    "__gt__",
    "__ge__",
    "__hash__",
    # Numeric conversions
    "__bool__",
    "__complex__",
    "__int__",
    "__float__",
    "__index__",
    "__round__",
    "__trunc__",
    "__floor__",
    "__ceil__",
    # Context managers.
    "__enter__",
    "__exit__",
    # Async tasks.
    "__await__",
    # Async iterators.
    "__aiter__",
    "__anext__",
    # Async context managers.
    "__aenter__",
    "__aexit__",
    # Formatting.
    "__repr__",
    "__str__",
    "__bytes__",
    "__format__",
]


def _statement_text_sorted_class(statement):
    head_text, body_statements = split_class(statement)
    return (
        head_text
        + "\n"
        + "\n".join(
            statement_text(body_statement)
            for body_statement in body_statements
        )
    )


def statement_text_sorted(statement):
    node = statement_node(statement)
    if isinstance(node, ast.ClassDef):
        return _statement_text_sorted_class(statement)
    return statement_text(statement)


def _optimize(statements, graph, *, key=lambda value: value):
    statements = statements.copy()

    def _swap(a, b):
        if a in graph.dependencies[b]:
            return False

        if key(a) < key(b):
            return False
        return True

    # Bubble sort will only move items one step at a time, meaning that we can
    # make sure nothing ever moves past something that depends on it.  The
    # builtin `sorted` function, while much faster, might result in us breaking
    # the topological sort.
    bubble_sort(statements, _swap)

    return statements


def ssort(text, *, filename="<unknown>"):
    statements = list(split(text, filename=filename))

    graph = statements_graph(statements)

    replace_cycles(graph, key=sort_key_from_iter(statements))

    sorted_statements = topological_sort(graph)

    sorted_statements = _optimize(
        sorted_statements, graph, key=sort_key_from_iter(statements)
    )

    assert is_topologically_sorted(sorted_statements, graph)

    return (
        "\n".join(
            statement_text_sorted(statement) for statement in sorted_statements
        )
        + "\n"
    )
