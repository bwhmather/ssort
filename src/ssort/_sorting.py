def _replace_cycles(dependencies_table):
    """
    Finds all cycles and replaces them with forward links that keep them from
    being re-ordered.
    """
    result = []
    for statement, dependencies in enumerate(dependencies_table):
        result.append(
            [
                dependency
                for dependency in dependencies
                if dependency != statement
            ]
        )
    return result


def _reverse_links(table):
    reversed_table = [[] for _ in range(len(table))]

    for node, linked_nodes in enumerate(table):
        for linked_node in linked_nodes:
            reversed_table[linked_node].append(node)

    return reversed_table


def _is_topologically_sorted(statements, dependencies_table):
    visited = set()
    for statement in statements:
        visited.add(statement)
        for dependency in dependencies_table[statement]:
            if dependency not in visited:
                return False
    return True


def _topological_sort(dependencies_table):
    dependants_table = _reverse_links(dependencies_table)

    pending = {
        statement
        for statement, dependencies in enumerate(dependencies_table)
        if not dependencies
    }

    # Create a mutable copy of the dependencies table that we can pop edges
    # from as we traverse them.
    graph = [set(dependencies) for dependencies in dependencies_table]

    result = []
    while pending:
        statement = pending.pop()
        for dependant in dependants_table[statement]:
            graph[dependant].discard(statement)
            if not graph[dependant]:
                pending.add(dependant)

        result.append(statement)

    assert len(result) == len(dependencies_table)
    assert _is_topologically_sorted(result, dependencies_table)

    return result


def bubble_sort(array, swap):
    n = len(array)
    while n > 1:
        next_n = 0
        for i in range(1, n):
            if swap(array[i - 1], array[i]):
                array[i - 1], array[i] = array[i], array[i - 1]
                next_n = i
        n = next_n


def bubble_sorted(array, swap):
    array = array.copy()
    bubble_sort(array, swap)
    return array


def _optimize(statements, dependencies_table):
    def _swap(a, b):
        if a in dependencies_table[b]:
            return False
        if a < b:
            return False
        return True

    # Bubble sort will only move items one step at a time, meaning that we can
    # make sure nothing ever moves past something that depends on it.  The
    # builtin `sorted` function, while much faster, might result in us breaking
    # the topological sort.
    return bubble_sorted(statements, _swap)


def sort(dependencies_table):
    dag_table = _replace_cycles(dependencies_table)
    sorted_statements = _topological_sort(dag_table)
    sorted_statements = _optimize(sorted_statements, dag_table)
    assert _is_topologically_sorted(sorted_statements, dag_table)
    return sorted_statements
