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


def _optimize(statements, dependencies_table):
    # TODO bubble sort
    return statements


def sort(dependencies_table):
    dag_table = _replace_cycles(dependencies_table)
    sorted_statements = _topological_sort(dag_table)
    return _optimize(sorted_statements, dag_table)
