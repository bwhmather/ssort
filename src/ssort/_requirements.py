from __future__ import annotations

import ast
import dataclasses
import enum
import sys
from typing import Iterable

from ssort._ast import iter_child_nodes
from ssort._bindings import get_bindings
from ssort._builtins import CLASS_BUILTINS
from ssort._utils import single_dispatch


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


@single_dispatch
def get_requirements(node: ast.AST) -> Iterable[Requirement]:
    for child in iter_child_nodes(node):
        yield from get_requirements(child)


def _get_requirements_from_nodes(
    nodes: Iterable[ast.AST],
) -> Iterable[Requirement]:
    for node in nodes:
        yield from get_requirements(node)


def _get_scope_from_arguments(args: ast.arguments) -> set[str]:
    scope: set[str] = set()
    scope.update(arg.arg for arg in args.posonlyargs)
    scope.update(arg.arg for arg in args.args)  # Arghhh.
    if args.vararg:
        scope.add(args.vararg.arg)
    scope.update(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        scope.add(args.kwarg.arg)
    return scope


if sys.version_info >= (3, 12):

    def _get_scope_from_type_params(
        type_params: list[ast.type_param],
    ) -> set[str]:
        return set(type_param.name for type_param in type_params)  # type: ignore[attr-defined]

    @get_requirements.register(ast.TypeAlias)
    def _get_requirements_for_type_alias(
        node: ast.TypeAlias,
    ) -> Iterable[Requirement]:
        scope = _get_scope_from_type_params(node.type_params)
        for requirement in _get_requirements_from_nodes(node.type_params):
            if requirement.name not in scope:
                yield requirement

        scope.add(node.name.id)
        for requirement in get_requirements(node.value):
            if not requirement.deferred:
                requirement = dataclasses.replace(requirement, deferred=True)
            if requirement.name not in scope:
                yield requirement


@get_requirements.register(ast.FunctionDef)
@get_requirements.register(ast.AsyncFunctionDef)
def _get_requirements_for_function_def(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Iterable[Requirement]:
    yield from _get_requirements_from_nodes(node.decorator_list)

    scope: set[str] = set()
    if sys.version_info >= (3, 12):
        scope.update(_get_scope_from_type_params(node.type_params))
        for requirement in _get_requirements_from_nodes(node.type_params):
            if requirement.name not in scope:
                yield requirement

    for requirement in get_requirements(node.args):
        if requirement.name not in scope:
            yield requirement

    if node.returns is not None:
        for requirement in get_requirements(node.returns):
            if requirement.name not in scope:
                yield requirement

    scope.update(_get_scope_from_arguments(node.args))

    requirements = []
    for statement in node.body:
        scope.update(get_bindings(statement))
        for requirement in get_requirements(statement):
            if not requirement.deferred:
                requirement = dataclasses.replace(requirement, deferred=True)
            requirements.append(requirement)

    for requirement in requirements:
        if requirement.scope == Scope.GLOBAL:
            yield requirement
        elif requirement.scope == Scope.NONLOCAL:
            yield dataclasses.replace(requirement, scope=Scope.LOCAL)
        elif requirement.name not in scope:
            yield requirement


@get_requirements.register(ast.ClassDef)
def _get_requirements_for_class_def(
    node: ast.ClassDef,
) -> Iterable[Requirement]:
    yield from _get_requirements_from_nodes(node.decorator_list)

    scope: set[str] = set()
    if sys.version_info >= (3, 12):
        scope.update(_get_scope_from_type_params(node.type_params))
        for requirement in _get_requirements_from_nodes(node.type_params):
            if requirement.name not in scope:
                yield requirement

    for requirement in _get_requirements_from_nodes(node.bases):
        if requirement.name not in scope:
            yield requirement

    scope.update(CLASS_BUILTINS)

    for statement in node.body:
        for stmt_dep in get_requirements(statement):
            if stmt_dep.deferred or stmt_dep.name not in scope:
                yield stmt_dep

        scope.update(get_bindings(statement))


@get_requirements.register(ast.For)
@get_requirements.register(ast.AsyncFor)
def _get_requirements_for_for(
    node: ast.For | ast.AsyncFor,
) -> Iterable[Requirement]:
    bindings = set(get_bindings(node))

    yield from get_requirements(node.target)
    yield from get_requirements(node.iter)

    for requirement in _get_requirements_from_nodes(node.body):
        if requirement.name not in bindings:
            yield requirement

    for requirement in _get_requirements_from_nodes(node.orelse):
        if requirement.name not in bindings:
            yield requirement


@get_requirements.register(ast.With)
@get_requirements.register(ast.AsyncWith)
def _get_requirements_for_with(
    node: ast.With | ast.AsyncWith,
) -> Iterable[Requirement]:
    bindings = set(get_bindings(node))

    yield from _get_requirements_from_nodes(node.items)

    for requirement in _get_requirements_from_nodes(node.body):
        if requirement.name not in bindings:
            yield requirement


@get_requirements.register(ast.Global)
def _get_requirements_for_global(node: ast.Global) -> Iterable[Requirement]:
    for name in node.names:
        yield Requirement(
            name=name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            scope=Scope.GLOBAL,
        )


@get_requirements.register(ast.Nonlocal)
def _get_requirements_for_nonlocal(
    node: ast.Nonlocal,
) -> Iterable[Requirement]:
    for name in node.names:
        yield Requirement(
            name=name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            scope=Scope.NONLOCAL,
        )


@get_requirements.register(ast.Lambda)
def _get_requirements_for_lambda(node: ast.Lambda) -> Iterable[Requirement]:
    yield from get_requirements(node.args)
    scope = _get_scope_from_arguments(node.args)
    scope.update(get_bindings(node.body))
    for requirement in get_requirements(node.body):
        if requirement.name not in scope:
            yield requirement


@get_requirements.register(ast.ListComp)
@get_requirements.register(ast.SetComp)
@get_requirements.register(ast.DictComp)
@get_requirements.register(ast.GeneratorExp)
def _get_requirements_for_comp(
    node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp,
) -> Iterable[Requirement]:
    bindings = {
        binding
        for generator in node.generators
        for binding in get_bindings(generator.target)
    }
    for child in iter_child_nodes(node):
        for requirement in get_requirements(child):
            if requirement.name not in bindings:
                yield requirement


@get_requirements.register(ast.Name)
def _get_requirements_for_name(node: ast.Name) -> Iterable[Requirement]:
    if isinstance(node.ctx, (ast.Load, ast.Del)):
        yield Requirement(
            name=node.id, lineno=node.lineno, col_offset=node.col_offset
        )
