from __future__ import annotations

import ast
from typing import Sequence

from ._node_visitor import SmartNodeVisitor

__all__ = ["get_bindings"]


class Bindings(SmartNodeVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        self.smart_visit(node.decorator_list)
        self.smart_append(node.name)
        # body is missing
        self.smart_visit(node.args)
        self.smart_visit(node.returns)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        self.smart_visit(node.decorator_list)
        self.smart_visit(node.bases)
        self.smart_visit(node.keywords)
        self.smart_append(node.name)
        # missing keywords, starargs, body

    def visit_Import(self, node):
        for name in node.names:
            if name.asname:
                self.smart_append(name.asname)
            else:
                root, *rest = name.name.split(".", 1)
                self.smart_append(root)

    def visit_ImportFrom(self, node):
        for name in node.names:
            self.smart_append(name.asname if name.asname else name.name)

    def visit_Global(self, node: ast.Global | ast.Nonlocal):
        self.smart_append(node.names)

    visit_Nonlocal = visit_Global

    def visit_Lambda(self, node):
        self.smart_visit(node.args)

    # def visit_alias(self, node: ast.alias):
    #     self.smart_append(node.asname if node.asname else node.name)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            self.smart_append(node.id)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.smart_visit(node.type)
        self.smart_append(node.name)
        self.smart_visit(node.body)

    def visit_MatchStar(self, node: ast.MatchStar):
        self.smart_append(node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping):
        self.smart_visit(node.keys)
        self.smart_visit(node.patterns)
        self.smart_append(node.rest)

    def visit_MatchAs(self, node: ast.MatchAs):
        self.smart_visit(node.pattern)
        self.smart_append(node.name)


def get_bindings(node: ast.AST):
    bindings = Bindings()
    bindings.visit(node)
    yield from bindings.stack
