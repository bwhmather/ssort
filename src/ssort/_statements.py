from __future__ import annotations

import ast
from typing import Iterable

from ssort._bindings import get_bindings
from ssort._method_requirements import get_method_requirements
from ssort._requirements import Requirement, get_requirements


class Statement:
    def __init__(
        self, *, text: str, node: ast.AST, start_row: int, start_col: int
    ) -> None:
        self._text = text
        self._node = node
        self._start_row = start_row
        self._start_col = start_col

    def __repr__(self) -> str:
        return f"<Statement text={self._text!r}>"


def statement_node(statement: Statement) -> ast.AST:
    return statement._node


def statement_text(statement: Statement) -> str:
    return statement._text


def statement_text_padded(statement: Statement) -> str:
    """
    Return the statement text padded with leading whitespace so that
    coordinates in the ast match up with coordinates in the text.
    """
    return (
        ("\n" * statement._start_row)
        + (" " * statement._start_col)
        + statement._text
    )


def statement_requirements(statement: Statement) -> Iterable[Requirement]:
    """
    Returns an iterable yielding Requirement objects describing the bindings
    that a statement references.
    """
    return get_requirements(statement_node(statement))


def statement_method_requirements(statement: Statement) -> Iterable[str]:
    """
    Returns an iterable yielding the names of attributes of the `self` parameter
    that a statement depends on.
    """
    return get_method_requirements(statement_node(statement))


def statement_bindings(statement: Statement) -> Iterable[str]:
    """
    Returns an iterable yielding the names bound by a statement.
    """
    return get_bindings(statement_node(statement))
