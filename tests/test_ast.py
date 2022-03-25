from __future__ import annotations

import ast
import sys
from typing import Iterable

import pytest

from ssort._ast import iter_child_nodes

_deprecated_node_types = (ast.AugLoad, ast.AugStore, ast.Param, ast.Suite)

if sys.version_info >= (3, 9):
    _deprecated_node_types += (ast.Index, ast.ExtSlice)

_ignored_node_types = (
    ast.expr_context,
    ast.boolop,
    ast.operator,
    ast.unaryop,
    ast.cmpop,
)


def _nodes_types(
    node_type: type[ast.AST] = ast.AST,
) -> Iterable[type[ast.AST]]:
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


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    node_types = list(_nodes_types())
    nodes = [node_type() for node_type in node_types]
    ids = [node_type.__name__ for node_type in node_types]

    metafunc.parametrize("node", nodes, ids=ids)


def test_iter_child_nodes_is_implemented(node: ast.AST) -> None:
    iter_child_nodes(node)
