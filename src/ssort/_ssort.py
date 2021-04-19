from ssort._bubble_sort import bubble_sort
from ssort._dependencies import statements_graph
from ssort._graphs import (
    is_topologically_sorted,
    replace_cycles,
    topological_sort,
)
from ssort._parsing import split
from ssort._statements import statement_text
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
    statements = list(split(text, filename=filename))

    graph = statements_graph(statements)

    replace_cycles(graph, key=sort_key_from_iter(statements))

    sorted_statements = topological_sort(graph)

    sorted_statements = _optimize(
        sorted_statements, graph, key=sort_key_from_iter(statements)
    )

    assert is_topologically_sorted(sorted_statements, graph)

    return (
        "\n".join(statement_text(statement) for statement in sorted_statements)
        + "\n"
    )
