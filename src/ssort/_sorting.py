from ssort._bubble_sort import bubble_sort
from ssort._graphs import (
    Graph,
    is_topologically_sorted,
    replace_cycles,
    topological_sort,
)


def _optimize(statements, graph):
    statements = statements.copy()

    def _swap(a, b):
        if a in graph.dependencies[b]:
            return False
        if a < b:
            return False
        return True

    # Bubble sort will only move items one step at a time, meaning that we can
    # make sure nothing ever moves past something that depends on it.  The
    # builtin `sorted` function, while much faster, might result in us breaking
    # the topological sort.
    bubble_sort(statements, _swap)

    return statements


def sort(dependencies_table):
    graph = Graph(dependencies_table)
    replace_cycles(graph)
    sorted_statements = topological_sort(graph)
    sorted_statements = _optimize(sorted_statements, graph)
    assert is_topologically_sorted(sorted_statements, graph)
    return sorted_statements
