import ast
import functools


@functools.singledispatch
def get_bindings(node):
    return []


@get_bindings.register(ast.FunctionDef)
def _get_bindings_for_function_def(node):
    return [node.name]


@get_bindings.register(ast.ClassDef)
def _get_bindings_for_class_def(node):
    return [node.name]


@functools.singledispatch
def _flatten_target(node):
    raise NotImplementedError()


@_flatten_target.register(ast.Name)
def _flatten_target_name(node):
    assert isinstance(node.ctx, ast.Store)
    return [node.id]


@_flatten_target.register(ast.Starred)
def _flatten_target_starred(node):
    assert isinstance(node.ctx, ast.Store)
    return _flatten_target(node.value)


@_flatten_target.register(ast.Tuple)
def _flatten_target_tuple(node):
    assert isinstance(node.ctx, ast.Store)
    targets = []
    for element in node.elts:
        targets += _flatten_target(element)
    return targets


@get_bindings.register(ast.Assign)
def _get_bindings_for_assign(node):
    bindings = []
    for target in node.targets:
        bindings += _flatten_target(target)

    return bindings


@get_bindings.register(ast.ImportFrom)
def _get_bindings_for_import_from(node):
    return [name.asname if name.asname else name.name for name in node.names]


@get_bindings.register(ast.Import)
def _get_bindings_for_import(node):
    return [name.asname if name.asname else name.name for name in node.names]
