class Graph:
    def __init__(self):
        self.nodes = set()
        self.dependencies = {}
        self.dependants = {}

    @classmethod
    def from_dependencies(cls, nodes, get_dependencies):
        graph = cls()
        for node in nodes:
            graph.add_node(node)
            for dependency in get_dependencies(node):
                graph.add_node(dependency)
                graph.add_dependency(node, dependency)
        return graph

    def add_node(self, identifier):
        if identifier not in self.nodes:
            self.nodes.add(identifier)
            self.dependencies[identifier] = set()
            self.dependants[identifier] = set()

    def add_dependency(self, node, dependency):
        assert node in self.nodes
        assert dependency in self.nodes

        self.dependencies[node].add(dependency)
        self.dependants[dependency].add(node)

    def remove_node(self, node):
        self.nodes.discard(node)
        del self.dependencies[node]
        del self.dependants[node]

        for other in self.nodes:
            self.dependencies[other].discard(node)
            self.dependants[other].discard(node)

    def remove_dependency(self, node, dependency):
        assert node in self.nodes
        assert dependency in self.nodes

        self.dependencies[node].discard(dependency)
        self.dependants[dependency].discard(node)

    def copy(self):
        return Graph.from_dependencies(
            self.nodes, self.dependencies.__getitem__
        )


def _remove_self_references(graph):
    for node in graph.nodes:
        graph.remove_dependency(node, node)


def _find_cycle(graph):
    processed = set()
    for node in graph.nodes:
        if node in processed:
            continue

        in_stack = {node}
        stack = [(node, set(graph.dependencies[node]))]

        while stack:
            top_node, top_dependencies = stack[-1]

            if not top_dependencies:
                processed.add(top_node)
                in_stack.remove(top_node)
                stack.pop()
                continue

            dependency = top_dependencies.pop()
            if dependency in in_stack:
                cycle = [dependency]
                while stack[-1][0] != dependency:
                    cycle.append(stack[-1][0])
                    stack.pop()
                return cycle
            if dependency not in processed:
                stack.append((dependency, set(graph.dependencies[dependency])))
                in_stack.add(dependency)


def replace_cycles(graph, *, key):
    """
    Finds all cycles and replaces them with forward links that keep them from
    being re-ordered.
    """
    _remove_self_references(graph)
    while True:
        cycle = _find_cycle(graph)
        if not cycle:
            break

        for node in cycle:
            for dependency in cycle:
                graph.remove_dependency(node, dependency)

        # TODO this is a bit of an abstraction leak.  Need a better way to tell
        # this function what the safe order is.
        nodes = iter(sorted(cycle, key=key))
        prev = next(nodes)
        for node in nodes:
            graph.add_dependency(node, prev)
            prev = node


def is_topologically_sorted(nodes, graph):
    visited = set()
    for node in nodes:
        visited.add(node)
        for dependency in graph.dependencies[node]:
            if dependency not in visited:
                return False
    return True


def topological_sort(graph):
    # Create a mutable copy of the graph so that we can pop edges from it as we
    # traverse.
    remaining = graph.copy()

    pending = {node for node in graph.nodes if not graph.dependencies[node]}

    result = []
    while pending:
        node = pending.pop()
        dependants = set(remaining.dependants[node])
        remaining.remove_node(node)

        for dependant in dependants:
            if not remaining.dependencies[dependant]:
                pending.add(dependant)

        result.append(node)

    assert not remaining.nodes
    assert is_topologically_sorted(result, graph)

    return result
