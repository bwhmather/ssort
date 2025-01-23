from __future__ import annotations

import ast
from typing import Iterable

import pytest

from ssort._ast import iter_child_nodes

_deprecated_node_types: tuple[type[ast.AST], ...] = (
    ast.AugLoad,
    ast.AugStore,
    ast.Param,
    ast.Suite,
    ast.Index,
    ast.ExtSlice,
)

_ignored_node_types: tuple[type[ast.AST], ...] = (
    ast.expr_context,
    ast.boolop,
    ast.operator,
    ast.unaryop,
    ast.cmpop,
)


def _nodes_types(
    node_type: type[ast.AST] = ast.AST,
) -> Iterable[type[ast.AST]]:
    # coverage package adds a coverage.parser.NodeList subclass
    if node_type.__module__ != "ast":
        return

    # Skip deprecated AST nodes.
    if issubclass(node_type, _deprecated_node_types):
        return

    # Skip ignored AST nodes.
    if issubclass(node_type, _ignored_node_types):
        return

    subclasses = node_type.__subclasses__()
    if subclasses:
        # Note that we do not yield the node_type if it has any subclasses.
        # This is because AST base classes are used for categorical purposes
        # only and are not intended to be instantiated.
        for subclass in subclasses:
            yield from _nodes_types(subclass)
    else:
        yield node_type


def _instantiate_node(node_type: type[ast.AST]) -> ast.AST:
    # AST node fields are either strings or iterables of child AST nodes. The
    # empty string satisfies both those requirements.
    return node_type(*([""] * len(node_type._fields)))


def parametrize_nodes() -> pytest.MarkDecorator:
    node_types = list(_nodes_types())
    nodes = [_instantiate_node(node_type) for node_type in node_types]
    ids = [node_type.__name__ for node_type in node_types]

    return pytest.mark.parametrize("node", nodes, ids=ids)


def test_iter_child_nodes_is_not_implemented_for_none() -> None:
    with pytest.raises(NotImplementedError):
        iter_child_nodes(None)


@parametrize_nodes()
def test_iter_child_nodes_is_implemented(node: ast.AST) -> None:
    list(iter_child_nodes(node))
