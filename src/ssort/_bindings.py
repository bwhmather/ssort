from __future__ import annotations

import ast
from typing import Iterable

from ssort._ast import iter_child_nodes, node_dispatch


@node_dispatch
def get_bindings(node: ast.AST) -> Iterable[str]:
    for child in iter_child_nodes(node):
        yield from get_bindings(child)


@get_bindings.register(ast.FunctionDef, ast.AsyncFunctionDef)
def _get_bindings_for_function_def(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Iterable[str]:
    for decorator in node.decorator_list:
        yield from get_bindings(decorator)
    yield node.name
    yield from get_bindings(node.args)
    if node.returns is not None:
        yield from get_bindings(node.returns)


@get_bindings.register(ast.ClassDef)
def _get_bindings_for_class_def(node: ast.ClassDef) -> Iterable[str]:
    for decorator in node.decorator_list:
        yield from get_bindings(decorator)
    for base in node.bases:
        yield from get_bindings(base)
    for keyword in node.keywords:
        yield from get_bindings(keyword.value)
    yield node.name


@get_bindings.register(ast.Import)
def _get_bindings_for_import(node: ast.Import) -> Iterable[str]:
    for name in node.names:
        if name.asname:
            yield name.asname
        else:
            root, *rest = name.name.split(".", 1)
            yield root


@get_bindings.register(ast.ImportFrom)
def _get_bindings_for_import_from(node: ast.ImportFrom) -> Iterable[str]:
    for name in node.names:
        yield name.asname if name.asname else name.name


@get_bindings.register(ast.Global)
def _get_bindings_for_global(node: ast.Global) -> Iterable[str]:
    yield from node.names


@get_bindings.register(ast.Nonlocal)
def _get_bindings_for_nonlocal(node: ast.Nonlocal) -> Iterable[str]:
    yield from node.names


@get_bindings.register(ast.Lambda)
def _get_bindings_for_lambda(node: ast.Lambda) -> Iterable[str]:
    yield from get_bindings(node.args)


@get_bindings.register(ast.Name)
def _get_bindings_for_name(node: ast.Name) -> Iterable[str]:
    if isinstance(node.ctx, ast.Store):
        yield node.id


@get_bindings.register(ast.ExceptHandler)
def _get_bindings_for_except_handler(node: ast.ExceptHandler) -> Iterable[str]:
    if node.type:
        yield from get_bindings(node.type)
    if node.name:
        yield node.name
    for statement in node.body:
        yield from get_bindings(statement)
