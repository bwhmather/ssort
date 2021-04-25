import ast
import sys
import textwrap

from ssort._method_requirements import get_method_requirements


def _method_requirements(source):
    source = textwrap.dedent(source)
    root = ast.parse(source)
    assert len(root.body) == 1
    node = root.body[0]
    if sys.version_info >= (3, 9):
        print(ast.dump(node, include_attributes=True, indent=2))
    else:
        print(ast.dump(node, include_attributes=True))
    return list(get_method_requirements(node))


def test_staticmethod_requirements():
    reqs = _method_requirements(
        """
        @staticmethod
        def function():
            return Class.attr
        """
    )
    assert reqs == []


def test_classmethod_requirements():
    reqs = _method_requirements(
        """
        @classmethod
        def function(cls, arg, **kwargs):
            return cls.attr + arg.argattr
        """
    )
    assert reqs == ["attr"]


def test_method_requirements():
    reqs = _method_requirements(
        """
        def function(self, something):
            return self.a + self.b - something.other
        """
    )
    assert reqs == ["a", "b"]
