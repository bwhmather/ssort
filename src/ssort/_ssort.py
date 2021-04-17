import ast
import builtins
import sys

from ssort._bindings import get_bindings
from ssort._bubble_sort import bubble_sort
from ssort._graphs import (
    Graph,
    is_topologically_sorted,
    replace_cycles,
    topological_sort,
)
from ssort._parsing import Module, statement_node, statement_text
from ssort._requirements import get_requirements
from ssort._utils import memoize_weak

DEFAULT_SCOPE = {
    *builtins.__dict__,
    "__file__",
    "unicode",
    "long",
    "xrange",
    "buffer",
    "bytearray",
    "basestring",
    "WindowsError",
}


def statement_requirements(module, statement):
    """
    Returns an iterable yielding Requirement objects describing the bindings
    that a statement references.
    """
    return get_requirements(statement_node(module, statement))


def statement_bindings(module, statement):
    """
    Returns an iterable yielding the names bound by a statement.
    """
    return get_bindings(statement_node(module, statement))


def _dedup(values):
    output = []
    visited = set()
    for value in values:
        if value not in visited:
            output.append(value)
        visited.add(value)
    return output


@memoize_weak
def _statement_graph(module):
    """
    Returns a dictionary mapping from statements to lists of other statements.
    """
    # A dictionary mapping from names to the statements which bind them.
    scope = {}

    # A dictionary mapping from statements to lists of unresolved Requirements.
    unresolved = {}

    dependencies = {}
    dependants = {}

    for statement in module.statements():
        dependencies[statement] = []
        dependants[statement] = []
        unresolved[statement] = []

        for requirement in statement_requirements(module, statement):
            # TODO error if requirement is not deferred.
            if requirement.name in scope:
                dependencies[statement].append(scope[requirement.name])
                continue

            if requirement.name in DEFAULT_SCOPE:
                continue

            unresolved[statement].append(requirement)

        for name in statement_bindings(module, statement):
            scope[name] = statement

    # Patch up dependencies that couldn't be resolved immediately.
    for statement in module.statements():
        remaining = []
        for requirement in unresolved[statement]:
            if requirement.name in scope:
                dependencies[statement].append(scope[requirement.name])
            else:
                remaining.append(requirement.name)
        unresolved[statement] = remaining

    if "*" in scope:
        sys.stderr.write("WARNING: can't determine dependencies on * import")

        for statement in module.statements():
            for requirement in unresolved[statement]:
                dependencies[statement].append(scope["*"])

    else:
        for statement in module.statements():
            for requirement in unresolved[statement]:
                raise Exception(
                    f"Could not resolve requirement {requirement!r}"
                )

    for statement in module.statements():
        for dependency in dependencies[statement]:
            dependants[dependency].append(statement)

    for statement in module.statements():
        dependencies[statement] = _dedup(dependencies[statement])
        dependants[statement] = _dedup(dependants[statement])

    return dependencies, dependants


def statement_dependencies(module, statement):
    dependencies, dependants = _statement_graph(module)
    yield from dependencies[statement]


def statement_dependants(module, statement):
    dependencies, dependants = _statement_graph(module)
    yield from dependants[statement]


def statement_is_import(module, statement):
    node = statement_node(module, statement)
    return isinstance(node, (ast.Import, ast.ImportFrom))


def statement_is_assignment(module, statement):
    node = statement_node(module, statement)
    return isinstance(
        node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.NamedExpr)
    )


def _partition(values, predicate):
    passed = []
    failed = []

    for value in values:
        if predicate(value):
            passed.append(value)
        else:
            failed.append(value)
    return passed, failed


def _presort(module):
    statements = list(module.statements())
    output = []

    # TODO add dependency between imports and all non-import statements that
    # precede them.
    imports, statements = _partition(
        statements, lambda statement: statement_is_import(module, statement)
    )
    output += imports

    assignments, statements = _partition(
        statements,
        lambda statement: statement_is_assignment(module, statement),
    )
    output += assignments

    # Output all remaining statements with no dependants followed, recursively
    # by all of the statements that they depend on.
    # The goal here is to try to make it so that dependencies will always be
    # sorted close to the statements that depend on them, and in the order that
    # they are used.  We sort them after their dependants so that they get
    # squeezed down.
    free, statements = _partition(
        statements,
        lambda statement: not list(statement_dependants(module, statement)),
    )
    output += free

    output_set = set(output)
    cursor = 0
    while cursor < len(output):
        for dependency in statement_dependencies(module, output[cursor]):
            if dependency not in output_set:
                output.append(dependency)
                output_set.add(dependency)
        cursor += 1

    # Anything else was probably part of an isolated cycle.  Add it to the end
    # in the same order it came in.
    output += [
        statement for statement in statements if statement not in output_set
    ]

    return output


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


def _sort_key_from_iter(values):
    index = {statement: index for index, statement in enumerate(values)}
    key = lambda value: index[value]
    return key


def ssort(text, *, filename="<unknown>"):
    module = Module(text, filename=filename)

    presorted = _presort(module)

    graph = Graph.from_dependencies(
        module.statements(),
        lambda statement: statement_dependencies(module, statement),
    )
    replace_cycles(graph, key=_sort_key_from_iter(module.statements()))
    toposorted = topological_sort(graph)

    sorted_statements = _optimize(
        toposorted, graph, key=_sort_key_from_iter(presorted)
    )

    assert is_topologically_sorted(sorted_statements, graph)

    return (
        "\n".join(
            statement_text(module, statement)
            for statement in sorted_statements
        )
        + "\n"
    )
