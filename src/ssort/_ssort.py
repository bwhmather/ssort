import ast
import sys

from ssort._dependencies import (
    class_statements_initialisation_graph,
    class_statements_runtime_graph,
    statements_graph,
)
from ssort._graphs import (
    is_topologically_sorted,
    replace_cycles,
    topological_sort,
)
from ssort._parsing import split, split_class
from ssort._statements import (
    statement_bindings,
    statement_node,
    statement_text,
)
from ssort._utils import sort_key_from_iter

SPECIAL_PROPERTIES = [
    "__doc__",
    "__slots__",
]

LIFECYCLE_OPERATIONS = [
    # Lifecycle.
    "__new__",
    "__init__",
    "__del__",
    # Copying.
    "__copy__",
    "__deepcopy__",
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
    "__getitem__",
    "__setitem__",
    "__delitem__",
    "__missing__",
    "__iter__",
    "__reversed__",
    "__contains__",
    "__len__",
    "__length_hint__",
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
    # Pickling.
    "__getnewargs_ex__",
    "__reduce__",
    "__getstate__",
    "__setstate__",
    # Formatting.
    "__repr__",
    "__str__",
    "__bytes__",
    "__format__",
]


def _partition(values, predicate):
    passed = []
    failed = []

    for value in values:
        if predicate(value):
            passed.append(value)
        else:
            failed.append(value)
    return passed, failed


def _is_string(statement):
    expr_node = statement_node(statement)
    if not isinstance(expr_node, ast.Expr):
        return False

    node = expr_node.value
    if not isinstance(node, ast.Constant):
        return False

    if not isinstance(node.value, str):
        return False

    return True


def _is_special_property(statement):
    bindings = statement_bindings(statement)

    return any(binding in SPECIAL_PROPERTIES for binding in bindings)


def _is_lifecycle_operation(statement):
    bindings = statement_bindings(statement)

    return any(binding in LIFECYCLE_OPERATIONS for binding in bindings)


def _is_regular_operation(statement):
    bindings = statement_bindings(statement)

    return any(binding in REGULAR_OPERATIONS for binding in bindings)


def _is_property(statement):
    node = statement_node(statement)
    if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return False

    return True


def _statement_binding_sort_key(binding_key):
    def _safe_binding_key(binding):
        try:
            return binding_key(binding)
        except KeyError:
            return sys.maxsize

    def _key(statement):
        bindings = statement_bindings(statement)
        return min(_safe_binding_key(binding) for binding in bindings)

    return _key


def _statement_text_sorted_class(statement):
    head_text, statements = split_class(statement)

    # Take a snapshot of any hard dependencies between statements so that we can
    # restore them later.
    initialisation_graph = class_statements_initialisation_graph(statements)

    # === Split up the statements into high level groups =======================
    if _is_string(statements[0]):
        docstrings, statements = statements[:1], statements[1:]
    else:
        docstrings = []

    special_properties, statements = _partition(
        statements, _is_special_property
    )

    lifecycle_operations, statements = _partition(
        statements, _is_lifecycle_operation
    )

    regular_operations, statements = _partition(
        statements, _is_regular_operation
    )

    properties, statements = _partition(statements, _is_property)

    methods, statements = statements, []

    sorted_statements = []

    # === Join groups back together in the correct order =======================
    sorted_statements += docstrings

    # Special properties (in hard-coded order).
    sorted_statements += sorted(
        special_properties,
        key=_statement_binding_sort_key(
            sort_key_from_iter(SPECIAL_PROPERTIES)
        ),
    )

    # Regular properties (in original order).
    sorted_statements += properties

    # Special lifecycle methods (in hard-coded order).
    sorted_statements += sorted(
        lifecycle_operations,
        key=_statement_binding_sort_key(
            sort_key_from_iter(LIFECYCLE_OPERATIONS)
        ),
    )

    # Regular methods.
    sorted_statements += methods

    # Special operations (in hard-coded order).
    sorted_statements += sorted(
        regular_operations,
        key=_statement_binding_sort_key(
            sort_key_from_iter(REGULAR_OPERATIONS)
        ),
    )

    # === Re-sort based on dependencies between statements =====================

    # Fix any hard dependencies.
    sorted_statements = topological_sort(
        sorted_statements, graph=initialisation_graph
    )

    # Attempt to resolve soft dependencies, but with hard dependencies taking
    # priority, and keeping existing order where there are cycles.
    runtime_graph = class_statements_runtime_graph(sorted_statements)
    runtime_graph.update(initialisation_graph)
    replace_cycles(runtime_graph, key=sort_key_from_iter(sorted_statements))

    sorted_statements = topological_sort(
        sorted_statements, graph=runtime_graph
    )

    return (
        head_text
        + "\n"
        + "\n".join(
            statement_text_sorted(body_statement)
            for body_statement in sorted_statements
        )
    )


def statement_text_sorted(statement):
    node = statement_node(statement)
    if isinstance(node, ast.ClassDef):
        return _statement_text_sorted_class(statement)
    return statement_text(statement)


def ssort(text, *, filename="<unknown>"):
    statements = list(split(text, filename=filename))

    graph = statements_graph(statements)

    replace_cycles(graph, key=sort_key_from_iter(statements))

    sorted_statements = topological_sort(statements, graph=graph)

    assert is_topologically_sorted(sorted_statements, graph=graph)

    output = "\n".join(
        statement_text_sorted(statement) for statement in sorted_statements
    )
    if output:
        output += "\n"
    return output
