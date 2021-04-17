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


@memoize_weak
def _statement_graph(module):
    """
    Returns a dictionary mapping from statements to lists of other statements.
    """
    # A dictionary mapping from names to the statements which bind them.
    scope = {}

    # A dictionary mapping from statements to sets of unresolved Requirements.
    unresolved = {}

    dependencies = {}
    dependants = {}

    for statement in module.statements():
        dependencies[statement] = set()
        dependants[statement] = set()
        unresolved[statement] = list()

        for requirement in statement_requirements(module, statement):
            # TODO error if requirement is not deferred.
            if requirement.name in scope:
                dependencies[statement].add(scope[requirement.name])
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
                dependencies[statement].add(scope[requirement.name])
            else:
                remaining.append(requirement.name)
        unresolved[statement] = remaining

    if "*" in scope:
        sys.stderr.write("WARNING: can't determine dependencies on * import")

        for statement in module.statements():
            for requirement in unresolved[statement]:
                dependencies[statement].add(scope["*"])

    else:
        for statement in module.statements():
            for requirement in unresolved[statement]:
                raise Exception(
                    f"Could not resolve requirement {requirement!r}"
                )

    for statement in module.statements():
        for dependency in dependencies[statement]:
            dependants[dependency].add(statement)

    return dependencies, dependants


@memoize_weak
def statement_dependencies(module, statement):
    dependencies, dependants = _statement_graph(module)
    yield from dependencies[statement]


@memoize_weak
def statement_dependants(module, statement):
    dependencies, dependants = _statement_graph(module)
    yield from dependants[statement]


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
    module = Module(text, filename=filename)

    presorted = list(module.statements())
    index = {statement: index for index, statement in enumerate(presorted)}
    key = lambda value: index[value]

    graph = Graph.from_dependencies(
        module.statements(),
        lambda statement: statement_dependencies(module, statement),
    )
    replace_cycles(graph, key=key)
    toposorted = topological_sort(graph)

    sorted_statements = _optimize(toposorted, graph, key=key)

    assert is_topologically_sorted(sorted_statements, graph)
    return (
        "\n".join(
            statement_text(module, statement)
            for statement in sorted_statements
        )
        + "\n"
    )
