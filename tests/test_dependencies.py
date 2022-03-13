import textwrap

from ssort._dependencies import module_statements_graph
from ssort._parsing import parse


def _clean(source):
    return textwrap.dedent(source).strip() + "\n"


def _unreachable(*args, **kwargs):
    raise AssertionError("unreachable")


def test_dependencies_ordered_by_first_use():
    source = _clean(
        """
        def c():
            pass

        def a():
            map()
            b()
            c()

        def b():
            pass
        """
    )
    c, a, b = statements = list(parse(source, filename="<unknown>"))
    graph = module_statements_graph(
        statements, on_unresolved=_unreachable, on_wildcard_import=_unreachable
    )

    assert list(graph.dependencies[a]) == [b, c]
