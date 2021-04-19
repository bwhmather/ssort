from ssort._bubble_sort import bubble_sort
from ssort._dependencies import statement_dependencies
from ssort._graphs import (
    Graph,
    is_topologically_sorted,
    replace_cycles,
    topological_sort,
)
from ssort._modules import Module, statement_text
from ssort._utils import sort_key_from_iter


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

    graph = Graph.from_dependencies(
        module.statements(),
        lambda statement: statement_dependencies(module, statement),
    )
    replace_cycles(graph, key=sort_key_from_iter(module.statements()))

    toposorted = topological_sort(graph)

    sorted_statements = _optimize(
        toposorted, graph, key=sort_key_from_iter(module.statements())
    )

    assert is_topologically_sorted(sorted_statements, graph)

    return (
        "\n".join(
            statement_text(module, statement)
            for statement in sorted_statements
        )
        + "\n"
    )
