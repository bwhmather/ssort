import random

from ssort._graphs import Graph, topological_sort


def test_topological_sort_chain():
    graph = Graph()

    graph.add_node(1)
    graph.add_node(2)
    graph.add_node(3)
    graph.add_node(4)

    graph.add_dependency(2, 1)
    graph.add_dependency(3, 2)
    graph.add_dependency(4, 3)

    assert topological_sort(graph) == [1, 2, 3, 4]


def test_topological_sort_reversed_chain():
    graph = Graph()

    graph.add_node(1)
    graph.add_node(2)
    graph.add_node(3)
    graph.add_node(4)

    graph.add_dependency(1, 2)
    graph.add_dependency(2, 3)
    graph.add_dependency(3, 4)

    assert topological_sort(graph) == [4, 3, 2, 1]


def test_topological_sort_root():
    graph = Graph()

    graph.add_node(1)
    graph.add_node(2)
    graph.add_node(3)
    graph.add_node(4)

    graph.add_dependency(1, 4)
    graph.add_dependency(2, 4)
    graph.add_dependency(3, 4)

    assert topological_sort(graph) == [4, 1, 2, 3]


def test_topological_sort_tree():
    graph = Graph()

    graph.add_node(1)
    graph.add_node(2)
    graph.add_node(3)
    graph.add_node(4)
    graph.add_node(5)

    graph.add_dependency(3, 2)
    graph.add_dependency(5, 4)
    graph.add_dependency(5, 3)

    assert topological_sort(graph) == [1, 2, 3, 4, 5]


def test_unconnected_stable():
    nodes = list(range(1, 100))
    random.shuffle(nodes)

    graph = Graph()
    for node in nodes:
        graph.add_node(node)

    assert topological_sort(graph) == nodes


def test_random_stable():
    nodes = list(range(100))
    random.shuffle(nodes)

    graph = Graph()

    for node in nodes:
        graph.add_node(node)

    for _ in range(200):
        src_index = random.randrange(1, 100)
        tgt_index = random.randrange(src_index)
        graph.add_dependency(nodes[src_index], nodes[tgt_index])

    assert topological_sort(graph) == nodes
