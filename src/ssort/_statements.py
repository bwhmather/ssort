from __future__ import annotations

import ast
import functools

from ssort._bindings import get_bindings
from ssort._method_requirements import get_method_requirements
from ssort._requirements import Requirement, get_requirements


class Statement:
    def __init__(
        self, *, text: str, node: ast.AST, start_row: int, start_col: int
    ) -> None:
        self.text = text
        self.node = node
        self.start_row = start_row
        self.start_col = start_col

    @functools.cached_property
    def text_padded(self) -> str:
        """
        Return the statement text padded with leading whitespace so that
        coordinates in the ast match up with coordinates in the text.
        """
        return ("\n" * self.start_row) + (" " * self.start_col) + self.text

    @functools.cached_property
    def requirements(self) -> tuple[Requirement, ...]:
        """
        Returns an iterable yielding Requirement objects describing the
        bindings that a statement references.
        """
        return tuple(get_requirements(self.node))

    @functools.cached_property
    def method_requirements(self) -> tuple[str, ...]:
        """
        Returns an iterable yielding the names of attributes of the `self`
        parameter that a statement depends on.
        """
        return tuple(get_method_requirements(self.node))

    @functools.cached_property
    def bindings(self) -> tuple[str, ...]:
        """
        Returns an iterable yielding the names bound by a statement.
        """
        return tuple(get_bindings(self.node))

    def __repr__(self) -> str:
        return f"<Statement text={self.text!r}>"
