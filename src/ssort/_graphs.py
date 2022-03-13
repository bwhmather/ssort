from __future__ import annotations

from typing import Callable, Generic, Hashable, TypeVar

from ssort._utils import sort_key_from_iter

_T = TypeVar("_T", bound=Hashable)


class Graph(Generic[_T]):
    def __init__(self) -> None:
        self.nodes: list[_T] = []
        self.dependencies: dict[_T, list[_T]] = {}
        self.dependants: dict[_T, list[_T]] = {}

    def add_node(self, identifier: _T) -> None:
        if identifier not in self.nodes:
            self.nodes.append(identifier)
            self.dependencies[identifier] = []
            self.dependants[identifier] = []

    def add_dependency(self, node: _T, dependency: _T) -> None:
        assert dependency in self.nodes

        if dependency not in self.dependencies[node]:
            self.dependencies[node].append(dependency)
            self.dependants[dependency].append(node)

    def remove_node(self, node: _T) -> None:
        self.nodes.remove(node)
        del self.dependencies[node]
        del self.dependants[node]

        for other in self.nodes:
            try:
                self.dependencies[other].remove(node)
            except ValueError:
                pass

            try:
                self.dependants[other].remove(node)
            except ValueError:
                pass

    def remove_dependency(self, node: _T, dependency: _T) -> None:
        assert dependency in self.nodes

        try:
            self.dependencies[node].remove(dependency)
        except ValueError:
            pass

        try:
            self.dependants[dependency].remove(node)
        except ValueError:
            pass

    def update(self, other: Graph[_T]) -> None:
        for node in other.nodes:
            self.add_node(node)

        for node in other.nodes:
            for dependency in other.dependencies[node]:
                self.add_dependency(node, dependency)

    def copy(self) -> Graph[_T]:
        dup: Graph[_T] = Graph()
        dup.update(self)
        return dup


def _remove_self_references(graph: Graph[_T]) -> None:
    for node in graph.nodes:
        graph.remove_dependency(node, node)


def _find_cycle(graph: Graph[_T]) -> list[_T] | None:
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

    return None


def replace_cycles(graph: Graph[_T], *, key: Callable[[_T], int]) -> None:
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


def is_topologically_sorted(nodes: list[_T], graph: Graph[_T]) -> bool:
    visited = set()
    for node in nodes:
        visited.add(node)
        for dependency in graph.dependencies[node]:
            if dependency not in visited:
                return False
    return True


def topological_sort(
    target: Graph[_T] | list[_T], /, *, graph: Graph[_T] | None = None
) -> list[_T]:
    if graph is None:
        if not isinstance(target, Graph):
            raise TypeError("target must be a Graph")
        graph = target
        nodes = target.nodes
    else:
        if not isinstance(target, list):
            raise TypeError("target must be a list")
        nodes = target

    # Create a mutable copy of the graph so that we can pop edges from it as we
    # traverse.
    remaining = graph.copy()

    key = sort_key_from_iter(nodes)

    pending = [node for node in graph.nodes if not graph.dependants[node]]

    result = []
    while pending:
        pending = list(sorted(pending, key=key))
        node = pending.pop()
        dependencies = remaining.dependencies[node]
        remaining.remove_node(node)

        for dependency in dependencies:
            if not remaining.dependants[dependency]:
                if dependency not in pending:
                    pending.append(dependency)

        result.append(node)

    result.reverse()

    assert not remaining.nodes
    assert is_topologically_sorted(result, graph)

    return [node for node in result if node in nodes]
