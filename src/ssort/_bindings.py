from __future__ import annotations

import ast
from typing import Sequence

__all__ = ["get_bindings"]


class Bindings(ast.NodeVisitor):
    def __init__(self):
        self.stack = []

    def append(self, name: list[str] | str | None):
        if name is None:
            return

        if isinstance(name, list):
            self.stack.extend(name)

        else:
            self.stack.append(name)

    def flexible_visit(self, node: Sequence[ast.AST] | ast.AST | None):
        if node is None:
            return

        if isinstance(node, Sequence):
            for n in node:
                self.flexible_visit(n)
        else:
            self.visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        self.flexible_visit(node.decorator_list)
        self.append(node.name)
        # body is missing
        self.flexible_visit(node.args)
        self.flexible_visit(node.returns)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        self.flexible_visit(node.decorator_list)
        self.flexible_visit(node.bases)
        self.flexible_visit(node.keywords)
        self.append(node.name)
        # missing keywords, starargs, body

    def visit_Import(self, node):
        for name in node.names:
            if name.asname:
                self.append(name.asname)
            else:
                root, *rest = name.name.split(".", 1)
                self.append(root)

    def visit_ImportFrom(self, node):
        for name in node.names:
            self.append(name.asname if name.asname else name.name)

    def visit_Global(self, node: ast.Global | ast.Nonlocal):
        self.append(node.names)

    visit_Nonlocal = visit_Global

    def visit_Lambda(self, node):
        self.flexible_visit(node.args)

    # def visit_alias(self, node: ast.alias):
    #     self.append(node.asname if node.asname else node.name)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            self.append(node.id)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.flexible_visit(node.type)
        self.append(node.name)
        self.flexible_visit(node.body)

    def visit_MatchStar(self, node: ast.MatchStar):
        self.append(node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping):
        self.flexible_visit(node.keys)
        self.flexible_visit(node.patterns)
        self.append(node.rest)

    def visit_MatchAs(self, node: ast.MatchAs):
        self.flexible_visit(node.pattern)
        self.append(node.name)


def get_bindings(node: ast.AST):
    bindings = Bindings()
    bindings.visit(node)
    yield from bindings.stack
