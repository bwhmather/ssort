from __future__ import annotations

import ast
import functools
import typing


@functools.singledispatch
def get_bindings(node: ast.AST) -> typing.Iterable[str]:
    for _, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    yield from get_bindings(item)
        elif isinstance(value, ast.AST):
            yield from get_bindings(value)


@get_bindings.register(ast.ClassDef)
def _get_bindings_for_class_def(node: ast.ClassDef) -> typing.Iterable[str]:
    for decorator in node.decorator_list:
        yield from get_bindings(decorator)

    for base in node.bases:
        yield from get_bindings(base)

    for keyword in node.keywords:
        yield from get_bindings(keyword.value)

    yield node.name


@get_bindings.register(ast.ExceptHandler)
def _get_bindings_for_except_handler(
    node: ast.ExceptHandler,
) -> typing.Iterable[str]:
    if node.type:
        yield from get_bindings(node.type)

    if node.name:
        yield node.name

    for stmt in node.body:
        yield from get_bindings(stmt)


@get_bindings.register(ast.FunctionDef)
@get_bindings.register(ast.AsyncFunctionDef)
def _get_bindings_for_function_def(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> typing.Iterable[str]:
    for decorator in node.decorator_list:
        yield from get_bindings(decorator)

    yield node.name

    yield from get_bindings(node.args)

    if node.returns is not None:
        yield from get_bindings(node.returns)


@get_bindings.register(ast.Global)
def _get_bindings_for_global(node: ast.Global) -> typing.Iterable[str]:
    yield from node.names


@get_bindings.register(ast.Import)
def _get_bindings_for_import(node: ast.Import) -> typing.Iterable[str]:
    for name in node.names:
        if name.asname:
            yield name.asname
        else:
            root, *rest = name.name.split(".", 1)
            yield root


@get_bindings.register(ast.ImportFrom)
def _get_bindings_for_import_from(
    node: ast.ImportFrom,
) -> typing.Iterable[str]:
    for name in node.names:
        yield name.asname if name.asname else name.name


@get_bindings.register(ast.Lambda)
def _get_bindings_for_lambda(node: ast.Lambda) -> typing.Iterable[str]:
    yield from get_bindings(node.args)


@get_bindings.register(ast.Name)
def _get_bindings_for_name(node: ast.Name) -> typing.Iterable[str]:
    if isinstance(node.ctx, ast.Store):
        yield node.id


@get_bindings.register(ast.Nonlocal)
def _get_bindings_for_non_local(node: ast.Nonlocal) -> typing.Iterable[str]:
    yield from node.names
