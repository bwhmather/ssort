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
