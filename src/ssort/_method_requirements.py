from __future__ import annotations

import ast

__all__ = ["get_method_requirements"]


class SelfAccesses(ast.NodeVisitor):
    def __init__(self, variable: str):
        self.stack: list[str] = []
        self.variable = variable

    def visit_ClassDef(self, _: ast.ClassDef):
        # TODO
        return

    def visit_Attribute(self, node: ast.Attribute):
        if not isinstance(node.value, ast.Name):
            super().visit(node.value)
        elif isinstance(node.ctx, ast.Load) and node.value.id == self.variable:
            self.stack.append(node.attr)


class MethodRequirements(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        if not node.args.args:
            return

        self_arg = node.args.args[0].arg

        self_access = SelfAccesses(self_arg)
        self_access.visit(node)
        self.stack.extend(self_access.stack)

    visit_AsyncFunctionDef = visit_FunctionDef


def get_method_requirements(node: ast.AST):
    method_requirements = MethodRequirements()
    method_requirements.visit(node)
    yield from method_requirements.stack
