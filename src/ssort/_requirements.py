from __future__ import annotations

import ast
import dataclasses
import enum
from typing import Iterable

from ssort._bindings import get_bindings
from ssort._builtins import CLASS_BUILTINS
from ssort._visitor import NodeVisitor, register_visitor


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


def _get_scope_from_arguments(args: ast.arguments) -> set[str]:
    scope = set()
    scope.update(arg.arg for arg in args.posonlyargs)
    scope.update(arg.arg for arg in args.args)  # Arghhh.
    if args.vararg:
        scope.add(args.vararg.arg)
    scope.update(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        scope.add(args.kwarg.arg)
    return scope


class _RequirementsNodeVisitor(NodeVisitor[Requirement]):
    @register_visitor(ast.FunctionDef, ast.AsyncFunctionDef)
    def visit_function_def(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> Iterable[Requirement]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)

        yield from self.visit(node.args)

        if node.returns is not None:
            yield from self.visit(node.returns)

        scope = _get_scope_from_arguments(node.args)

        requirements = []
        for statement in node.body:
            scope.update(get_bindings(statement))
            for requirement in self.visit(statement):
                if not requirement.deferred:
                    requirement = dataclasses.replace(
                        requirement, deferred=True
                    )
                requirements.append(requirement)

        for requirement in requirements:
            if requirement.scope == Scope.GLOBAL:
                yield requirement
            elif requirement.scope == Scope.NONLOCAL:
                yield dataclasses.replace(requirement, scope=Scope.LOCAL)
            elif requirement.name not in scope:
                yield requirement

    @register_visitor(ast.ClassDef)
    def visit_class_def(self, node: ast.ClassDef) -> Iterable[Requirement]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)

        for base in node.bases:
            yield from self.visit(base)

        scope = set(CLASS_BUILTINS)

        for statement in node.body:
            for stmt_dep in self.visit(statement):
                if stmt_dep.deferred or stmt_dep.name not in scope:
                    yield stmt_dep

            scope.update(get_bindings(statement))

    @register_visitor(ast.For, ast.AsyncFor)
    def visit_for(self, node: ast.For | ast.AsyncFor) -> Iterable[Requirement]:
        bindings = set(get_bindings(node))

        yield from self.visit(node.iter)

        for stmt in node.body:
            for requirement in self.visit(stmt):
                if requirement.name not in bindings:
                    yield requirement

        for stmt in node.orelse:
            for requirement in self.visit(stmt):
                if requirement.name not in bindings:
                    yield requirement

    @register_visitor(ast.With, ast.AsyncWith)
    def visit_with(
        self, node: ast.With | ast.AsyncWith
    ) -> Iterable[Requirement]:
        bindings = set(get_bindings(node))

        for item in node.items:
            yield from self.visit(item)

        for stmt in node.body:
            for requirement in self.visit(stmt):
                if requirement.name not in bindings:
                    yield requirement

    @register_visitor(ast.Global)
    def visit_global(self, node: ast.Global) -> Iterable[Requirement]:
        for name in node.names:
            yield Requirement(
                name=name,
                lineno=node.lineno,
                col_offset=node.col_offset,
                scope=Scope.GLOBAL,
            )

    @register_visitor(ast.Nonlocal)
    def visit_nonlocal(self, node: ast.Nonlocal) -> Iterable[Requirement]:
        for name in node.names:
            yield Requirement(
                name=name,
                lineno=node.lineno,
                col_offset=node.col_offset,
                scope=Scope.NONLOCAL,
            )

    @register_visitor(ast.Lambda)
    def visit_lambda(self, node: ast.Lambda) -> Iterable[Requirement]:
        yield from self.visit(node.args)
        scope = _get_scope_from_arguments(node.args)
        for requirement in self.visit(node.body):
            if requirement.name not in scope:
                yield requirement

    @register_visitor(
        ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp
    )
    def vist_comp(self, node: ast.AST) -> Iterable[Requirement]:
        bindings = set(get_bindings(node))
        for requirement in self.generic_visit(node):
            if requirement.name not in bindings:
                yield requirement

    @register_visitor(ast.Name)
    def visit_name(self, node: ast.Name) -> Iterable[Requirement]:
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            yield Requirement(
                name=node.id, lineno=node.lineno, col_offset=node.col_offset
            )


_visitor = _RequirementsNodeVisitor()


def get_requirements(node: ast.AST) -> Iterable[Requirement]:
    return _visitor.visit(node)
