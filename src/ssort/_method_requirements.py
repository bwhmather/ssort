from __future__ import annotations

import ast
from typing import Iterable

from ssort._ast import iter_child_nodes
from ssort._utils import single_dispatch


@single_dispatch
def _get_attribute_accesses(node: ast.AST, variable: str) -> Iterable[str]:
    for child in iter_child_nodes(node):
        yield from _get_attribute_accesses(child, variable)


@_get_attribute_accesses.register(ast.ClassDef)
def _get_attribute_accesses_for_class_def(
    node: ast.ClassDef, variable: str
) -> Iterable[str]:
    # TODO
    return ()


@_get_attribute_accesses.register(ast.Attribute)
def _get_attribute_accesses_for_attribute(
    node: ast.Attribute, variable: str
) -> Iterable[str]:
    yield from _get_attribute_accesses(node.value, variable)
    if (
        isinstance(node.ctx, ast.Load)
        and isinstance(node.value, ast.Name)
        and node.value.id == variable
    ):
        yield node.attr


@single_dispatch
def get_method_requirements(node: ast.AST) -> Iterable[str]:
    return ()


@get_method_requirements.register(ast.FunctionDef)
@get_method_requirements.register(ast.AsyncFunctionDef)
def _get_method_requirements_for_function_def(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Iterable[str]:
    if not node.args.args:
        return

    self_arg = node.args.args[0].arg

    for statement in node.body:
        yield from _get_attribute_accesses(statement, self_arg)
