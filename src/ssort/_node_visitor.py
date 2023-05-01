import ast
from typing import Sequence


class SmartNodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.stack = []

    def smart_append(self, name: list[str] | str | None):
        if name is None:
            return

        if isinstance(name, list):
            self.stack.extend(name)

        else:
            self.stack.append(name)

    def smart_visit(self, node: Sequence[ast.AST] | ast.AST | None):
        if node is None:
            return

        if isinstance(node, Sequence):
            for n in node:
                self.smart_visit(n)
        else:
            self.visit(node)
