import textwrap

from ssort._dependencies import statement_dependencies
from ssort._modules import Module


def _clean(source):
    return textwrap.dedent(source).strip() + "\n"


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
    module = Module(source, filename="<unknown>")
    c, a, b = module.statements()

    assert list(statement_dependencies(module, a)) == [b, c]
