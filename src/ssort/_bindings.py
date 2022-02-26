import ast
import functools


@functools.singledispatch
def get_bindings(node):
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    yield from get_bindings(item)
        elif isinstance(value, ast.AST):
            yield from get_bindings(value)


@get_bindings.register(ast.FunctionDef)
@get_bindings.register(ast.AsyncFunctionDef)
def _get_bindings_for_function_def(node):
    """
    ..code:: python

        FunctionDef(
            identifier name,
            arguments args,
            stmt* body,
            expr* decorator_list,
            expr? returns,
            string? type_comment,
        )

    ..code:: python

        AsyncFunctionDef(
            identifier name,
            arguments args,
            stmt* body,
            expr* decorator_list,
            expr? returns,
            string? type_comment,
        )
    """
    for decorator in node.decorator_list:
        yield from get_bindings(decorator)

    yield node.name

    yield from get_bindings(node.args)

    if node.returns is not None:
        yield from get_bindings(node.returns)


@get_bindings.register(ast.ClassDef)
def _get_bindings_for_class_def(node):
    """
    ..code:: python

        ClassDef(
            identifier name,
            expr* bases,
            keyword* keywords,
            stmt* body,
            expr* decorator_list,
        )
    """
    for decorator in node.decorator_list:
        yield from get_bindings(decorator)

    for base in node.bases:
        yield from get_bindings(base)

    for keyword in node.keywords:
        yield from get_bindings(keyword.value)

    yield node.name


@get_bindings.register(ast.Name)
def _get_bindings_for_name(node):
    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    if isinstance(node.ctx, ast.Store):
        yield node.id


@get_bindings.register(ast.ExceptHandler)
def _get_bindings_for_except_handler(node):
    """
    ..code:: python

        ExceptHandler(expr? type, identifier? name, stmt* body)
    """
    if node.type:
        yield from get_bindings(node.type)

    if node.name:
        yield node.name

    for stmt in node.body:
        yield from get_bindings(stmt)


@get_bindings.register(ast.Import)
def _get_bindings_for_import(node):
    """
    ..code:: python

        Import(alias* names)
    """
    for name in node.names:
        if name.asname:
            yield name.asname
        else:
            root, *rest = name.name.split(".", 1)
            yield root


@get_bindings.register(ast.ImportFrom)
def _get_bindings_for_import_from(node):
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)
    """
    for name in node.names:
        yield name.asname if name.asname else name.name


@get_bindings.register(ast.Global)
def _get_bindings_for_global(node):
    """
    ..code:: python

        Global(identifier* names)
    """
    yield from node.names


@get_bindings.register(ast.Nonlocal)
def _get_bindings_for_non_local(node):
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    yield from node.names


@get_bindings.register(ast.Lambda)
def _get_bindings_for_lambda(node):
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    yield from get_bindings(node.args)
