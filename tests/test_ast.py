from __future__ import annotations

import ast
import sys
from typing import Iterable

import pytest

from ssort._ast import iter_child_nodes

_deprecated_node_types = {ast.AugLoad, ast.AugStore, ast.Param, ast.Suite}

if sys.version_info >= (3, 9):
    _deprecated_node_types.update({ast.Index, ast.ExtSlice})


def _nodes(node_type: type[ast.AST] = ast.AST) -> Iterable[ast.AST]:
    # Skip deprecated AST nodes.
    if node_type in _deprecated_node_types:
        return

    subclasses = node_type.__subclasses__()
    if subclasses:
        # Note that we do not yield the node_type if it has any subclasses.
        # This is because AST base classes are used for categorical purposes
        # only and are not intended to be instantiated.
        for subclass in subclasses:
            yield from _nodes(subclass)
    else:
        yield node_type()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    nodes = list(_nodes())
    ids = [type(node).__name__ for node in nodes]

    metafunc.parametrize("node", nodes, ids=ids)


def test_iter_child_nodes_is_implemented(node: ast.AST) -> None:
    iter_child_nodes(node)
