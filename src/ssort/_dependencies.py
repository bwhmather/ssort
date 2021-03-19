import ast
import functools

from ssort._bindings import get_bindings


@functools.singledispatch
def get_dependencies(node):
    return []


@get_dependencies.register(ast.Expr)
def _get_dependencies_for_expr(node):
    return get_dependencies(node.value)


@get_dependencies.register(ast.Attribute)
def _get_dependencies_for_attribute(node):
    return get_dependencies(node.value)


@get_dependencies.register(ast.Name)
def _get_dependencies_for_name(node):
    assert isinstance(node.ctx, ast.Load)
    return [node.id]


@get_dependencies.register(ast.Assign)
def _get_dependencies_for_assign(node):
    return get_dependencies(node.value)


@get_dependencies.register(ast.FunctionDef)
def _get_dependencies_for_function_def(node):
    dependencies = []
    for decorator in node.decorator_list:
        dependencies += get_dependencies(decorator)

    scope = set()
    scope.update(arg.arg for arg in node.args.args)  # Guh.
    if node.args.vararg:
        scope.update(node.args.vararg.arg)
    scope.update(arg.arg for arg in node.args.kwonlyargs)
    if node.args.kwarg:
        scope.update(node.args.kwarg.arg)

    for statement in node.body:
        scope.update(get_bindings(statement))
        dependencies += get_dependencies(statement)

    return [dependency for dependency in dependencies if dependency not in scope]


@get_dependencies.register(ast.Call)
def _get_dependencies_for_call(node):
    dependencies = get_dependencies(node.func)

    for arg in node.args:
        dependencies += get_dependencies(arg)

    for kwarg in node.keywords:
        dependencies += get_dependencies(kwarg.value)

    return dependencies


@get_dependencies.register(ast.Starred)
def _get_dependencies_for_starred(node):
    return get_dependencies(node.value)


@get_dependencies.register(ast.Tuple)
def _get_dependencies_for_tuple(node):
    dependencies = []
    for element in node.elts:
        dependencies += get_dependencies(element)
    return dependencies


@get_dependencies.register(ast.BinOp)
def _get_dependencies_for_binop(node):
    return [
        *get_dependencies(node.left),
        *get_dependencies(node.right),
    ]


@get_dependencies.register(ast.UnaryOp)
def _get_dependencies_for_unary(node):
    return get_dependencies(node.operand)
