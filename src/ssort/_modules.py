import ast
import dataclasses
import weakref

from ssort._bindings import get_bindings
from ssort._parsing import split
from ssort._requirements import get_requirements


@dataclasses.dataclass(frozen=True)
class Statement:
    _module: weakref.ref
    _node: ast.AST
    _text: str


class Module:
    def __init__(self, text, *, filename="<unknown>"):
        self_ref = weakref.ref(self)
        self._statements = [
            Statement(_module=self_ref, _node=node, _text=text)
            for text, node in split(text)
        ]

    def statements(self):
        yield from self._statements


def statement_node(module, statement):
    assert statement._module() == module
    return statement._node


def statement_text(module, statement):
    assert statement._module() == module
    return statement._text


def statement_requirements(module, statement):
    """
    Returns an iterable yielding Requirement objects describing the bindings
    that a statement references.
    """
    return get_requirements(statement_node(module, statement))


def statement_bindings(module, statement):
    """
    Returns an iterable yielding the names bound by a statement.
    """
    return get_bindings(statement_node(module, statement))


def statement_is_import(module, statement):
    node = statement_node(module, statement)
    return isinstance(node, (ast.Import, ast.ImportFrom))


def statement_is_assignment(module, statement):
    node = statement_node(module, statement)
    return isinstance(
        node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.NamedExpr)
    )
