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


@get_bindings.register(ast.Assign)
def _get_bindings_for_assign(node):
    bindings = []
    for target in node.targets:
        bindings += get_bindings(target)
    return bindings


@get_bindings.register(ast.Import)
def _get_bindingsfor_import(node):
    return [name.asname if name.asname else name.name for name in node.names]
