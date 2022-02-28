from __future__ import annotations

import ast
from typing import Iterable

from ssort._visitor import NodeVisitor


class _BindingsNodeVisitor(NodeVisitor[str]):
    def visit_function_def(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> Iterable[str]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        yield node.name
        yield from self.visit(node.args)
        if node.returns is not None:
            yield from self.visit(node.returns)

    def visit_class_def(self, node: ast.ClassDef) -> Iterable[str]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        for base in node.bases:
            yield from self.visit(base)
        for keyword in node.keywords:
            yield from self.visit(keyword.value)
        yield node.name

    def visit_import(self, node: ast.Import) -> Iterable[str]:
        for name in node.names:
            if name.asname:
                yield name.asname
            else:
                root, *rest = name.name.split(".", 1)
                yield root

    def visit_import_from(self, node: ast.ImportFrom) -> Iterable[str]:
        for name in node.names:
            yield name.asname if name.asname else name.name

    def visit_global(self, node: ast.Global) -> Iterable[str]:
        yield from node.names

    def visit_nonlocal(self, node: ast.Nonlocal) -> Iterable[str]:
        yield from node.names

    def visit_lambda(self, node: ast.Lambda) -> Iterable[str]:
        yield from self.visit(node.args)

    def visit_name(self, node: ast.Name) -> Iterable[str]:
        if isinstance(node.ctx, ast.Store):
            yield node.id

    def visit_except_handler(self, node: ast.ExceptHandler) -> Iterable[str]:
        if node.type:
            yield from self.visit(node.type)
        if node.name:
            yield node.name
        for statement in node.body:
            yield from self.visit(statement)


_visitor = _BindingsNodeVisitor()


def get_bindings(node: ast.AST) -> Iterable[str]:
    return _visitor.visit(node)
