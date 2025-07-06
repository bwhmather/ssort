import ast

from ssort._utils import single_dispatch


@single_dispatch
def is_overload(node):
    """
    Implements heuristic for guessing if a top level statement is likely to
    represent an alternative type signature marked with `@typing.overload`.
    """
    return False


def _has_overload_decorator(node):
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "overload":
            return True
        if (
            isinstance(decorator, ast.Attribute)
            and decorator.attr == "overload"
        ):
            return True
    return False


def _has_empty_body(node):
    if len(node.body) != 1:
        return False
    if isinstance(node.body[0], ast.Expr):
        expr = node.body[0]
        if not isinstance(expr.value, ast.Constant):
            return False
        if expr.value.value is not Ellipsis:
            return False
        return True
    if isinstance(node.body[0], ast.Pass):
        return True
    return False


@is_overload.register(ast.FunctionDef)
@is_overload.register(ast.AsyncFunctionDef)
def _function_def_is_overload(node):
    if not _has_overload_decorator(node):
        return False
    if not _has_empty_body(node):
        return False
    return True
