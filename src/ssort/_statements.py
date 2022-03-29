from __future__ import annotations

import ast
from typing import Iterable

from ssort._bindings import get_bindings
from ssort._method_requirements import get_method_requirements
from ssort._requirements import Requirement, get_requirements
from ssort._utils import cached_method


class Statement:
    def __init__(
        self, *, text: str, node: ast.AST, start_row: int, start_col: int
    ) -> None:
        self.text = text
        self.node = node
        self.start_row = start_row
        self.start_col = start_col

    @cached_method
    def text_padded(self) -> str:
        """
        Return the statement text padded with leading whitespace so that
        coordinates in the ast match up with coordinates in the text.
        """
        return ("\n" * self.start_row) + (" " * self.start_col) + self.text

    @cached_method
    def requirements(self) -> Iterable[Requirement]:
        """
        Returns an iterable yielding Requirement objects describing the
        bindings that this statement references.
        """
        return tuple(get_requirements(self.node))

    @cached_method
    def method_requirements(self) -> Iterable[str]:
        """
        Returns an iterable yielding the names of attributes of the `self`
        parameter that this statement depends on.
        """
        return tuple(get_method_requirements(self.node))

    @cached_method
    def bindings(self) -> Iterable[str]:
        """
        Returns an iterable yielding the names bound by this statement.
        """
        return tuple(get_bindings(self.node))

    def __repr__(self) -> str:
        return f"<Statement text={self.text!r}>"
