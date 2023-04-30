from __future__ import annotations

import ast
import dataclasses
import enum
from typing import Sequence

from ssort._bindings import get_bindings
from ssort._builtins import CLASS_BUILTINS

__all__ = ["get_requirements", "Requirement"]


class Scope(enum.Enum):
    LOCAL = "LOCAL"
    NONLOCAL = "NONLOCAL"
    GLOBAL = "GLOBAL"


@dataclasses.dataclass(frozen=True)
class Requirement:
    name: str
    lineno: int
    col_offset: int
    deferred: bool = False
    scope: Scope = Scope.LOCAL


def get_scope_from_arguments(args: ast.arguments) -> set[str]:
    scope: set[str] = set()
    scope.update(arg.arg for arg in args.posonlyargs)
    scope.update(arg.arg for arg in args.args)  # Arghhh.
    if args.vararg:
        scope.add(args.vararg.arg)
    scope.update(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        scope.add(args.kwarg.arg)
    return scope


def get_requirements(node: ast.AST):
    requirements = Requirements()
    requirements.visit(node)
    yield from requirements.stack


class Requirements(ast.NodeVisitor):
    def __init__(self):
        self.stack = []

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
        self.flexible_visit(node.args)
        self.flexible_visit(node.returns)

        scope = get_scope_from_arguments(node.args)

        requirements = []
        for statement in node.body:
            scope.update(get_bindings(statement))
            for requirement in get_requirements(statement):
                if not requirement.deferred:
                    requirement = dataclasses.replace(
                        requirement, deferred=True
                    )
                requirements.append(requirement)

        for requirement in requirements:
            if requirement.scope == Scope.GLOBAL:
                self.stack.append(requirement)
            elif requirement.scope == Scope.NONLOCAL:
                self.stack.append(
                    dataclasses.replace(requirement, scope=Scope.LOCAL)
                )
            elif requirement.name not in scope:
                self.stack.append(requirement)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        self.flexible_visit(node.decorator_list)
        self.flexible_visit(node.bases)

        scope = set(CLASS_BUILTINS)

        for statement in node.body:
            for stmt_dep in get_requirements(statement):
                if stmt_dep.deferred or stmt_dep.name not in scope:
                    self.stack.append(stmt_dep)

            scope.update(get_bindings(statement))

    def visit_For(self, node: ast.For | ast.AsyncFor):
        bindings = set(get_bindings(node))

        self.flexible_visit(node.target)
        self.flexible_visit(node.iter)

        for stmt in node.body:
            for requirement in get_requirements(stmt):
                if requirement.name not in bindings:
                    self.stack.append(requirement)

        for stmt in node.orelse:
            for requirement in get_requirements(stmt):
                if requirement.name not in bindings:
                    self.stack.append(requirement)

    visit_AsyncFor = visit_For

    def visit_With(self, node: ast.With | ast.AsyncWith):
        bindings = set(get_bindings(node))

        self.flexible_visit(node.items)

        for stmt in node.body:
            for requirement in get_requirements(stmt):
                if requirement.name not in bindings:
                    self.stack.append(requirement)

    visit_AsyncWith = visit_With

    def visit_Global(self, node: ast.Global):
        for name in node.names:
            self.stack.append(
                Requirement(
                    name=name,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    scope=Scope.GLOBAL,
                )
            )

    def visit_Nonlocal(self, node: ast.Nonlocal):
        for name in node.names:
            self.stack.append(
                Requirement(
                    name=name,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    scope=Scope.NONLOCAL,
                )
            )

    def visit_Lambda(self, node: ast.Lambda):
        self.flexible_visit(node.args)

        scope = get_scope_from_arguments(node.args)
        scope.update(get_bindings(node.body))

        for requirement in get_requirements(node.body):
            if requirement.name not in scope:
                self.stack.append(requirement)

    def visit_ListComp(
        self,
        node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp,
    ):
        bindings = set(get_bindings(node))
        for child in ast.iter_child_nodes(node):
            for requirement in get_requirements(child):
                if requirement.name not in bindings:
                    self.stack.append(requirement)

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self.stack.append(
                Requirement(
                    name=node.id,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            )
