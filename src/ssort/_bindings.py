import ast
import functools
import sys


@functools.singledispatch
def get_bindings(node):
    raise NotImplementedError(
        f"could not find bindings for unsupported node {node!r} "
        f"at line {node.lineno}, column: {node.col_offset}"
    )


def _get_bindings_from_arguments(args):
    for arg in args.posonlyargs:
        if arg.annotation is None:
            continue
        yield from get_bindings(arg.annotation)

    for arg in args.args:
        if arg.annotation is None:
            continue
        yield from get_bindings(arg.annotation)

    if args.vararg is not None and args.vararg.annotation is not None:
        yield from get_bindings(args.vararg.annotation)

    for arg in args.kwonlyargs:
        if arg.annotation is None:
            continue
        yield from get_bindings(arg.annotation)

    if args.kwarg is not None and args.kwarg.annotation is not None:
        yield from get_bindings(args.kwarg.annotation)

    for default in args.defaults:
        yield from get_bindings(default)

    for default in args.kw_defaults:
        if default is None:
            continue

        yield from get_bindings(default)


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

    yield from _get_bindings_from_arguments(node.args)

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


@get_bindings.register(ast.Return)
def _get_bindings_for_return(node):
    """
    ..code:: python

        Return(expr? value)

    """
    return
    yield


@get_bindings.register(ast.Delete)
def _get_bindings_for_delete(node):
    """
    ..code:: python

        Delete(expr* targets)
    """
    return
    yield


@functools.singledispatch
def _flatten_target(node):
    raise NotImplementedError(f"not implemented for {node!r}")


@_flatten_target.register(ast.Name)
def _flatten_target_name(node):
    assert isinstance(node.ctx, ast.Store)
    yield node.id


@_flatten_target.register(ast.Starred)
def _flatten_target_starred(node):
    assert isinstance(node.ctx, ast.Store)
    yield from _flatten_target(node.value)


@_flatten_target.register(ast.Tuple)
def _flatten_target_tuple(node):
    assert isinstance(node.ctx, ast.Store)
    for element in node.elts:
        yield from _flatten_target(element)


@_flatten_target.register(ast.Subscript)
def _flatten_target_subscript(node):
    assert isinstance(node.ctx, ast.Store)
    return
    yield


@_flatten_target.register(ast.Attribute)
def _flatten_target_attribute(node):
    """
    ..code:: python

        Attribute(expr value, identifier attr, expr_context ctx)
    """
    assert isinstance(node.ctx, ast.Store)
    return
    yield


@_flatten_target.register(ast.List)
def _flatten_target_list(node):
    assert isinstance(node.ctx, ast.Store)
    for element in node.elts:
        yield from _flatten_target(element)


@get_bindings.register(ast.Assign)
def _get_bindings_for_assign(node):
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    yield from get_bindings(node.value)

    for target in node.targets:
        yield from _flatten_target(target)


@get_bindings.register(ast.AugAssign)
def _get_bindings_for_aug_assign(node):
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    yield from get_bindings(node.value)

    yield from _flatten_target(node.target)


@get_bindings.register(ast.AnnAssign)
def _get_bindings_for_ann_assign(node):
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    yield from get_bindings(node.annotation)

    if node.value is not None:
        yield from get_bindings(node.value)

    yield from _flatten_target(node.target)


@get_bindings.register(ast.For)
@get_bindings.register(ast.AsyncFor)
def _get_bindings_for_for(node):
    """
    ..code:: python

        # use 'orelse' because else is a keyword in target languages
        For(
            expr target,
            expr iter,
            stmt* body,
            stmt* orelse,
            string? type_comment,
        )

    ..code:: python

        AsyncFor(
            expr target,
            expr iter,
            stmt* body,
            stmt* orelse,
            string? type_comment,
        )
    """
    yield from get_bindings(node.iter)

    yield from _flatten_target(node.target)

    for stmt in node.body:
        yield from get_bindings(stmt)

    for stmt in node.orelse:
        yield from get_bindings(stmt)


@get_bindings.register(ast.While)
def _get_bindings_for_while(node):
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    yield from get_bindings(node.test)

    for stmt in node.body:
        yield from get_bindings(stmt)

    for stmt in node.orelse:
        yield from get_bindings(stmt)


@get_bindings.register(ast.If)
def _get_bindings_for_if(node):
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    yield from get_bindings(node.test)

    for stmt in node.body:
        yield from get_bindings(stmt)

    for stmt in node.orelse:
        yield from get_bindings(stmt)


@get_bindings.register(ast.With)
@get_bindings.register(ast.AsyncWith)
def _get_bindings_for_with(node):
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)

    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    for item in node.items:
        yield from get_bindings(item.context_expr)

        if item.optional_vars:
            yield from _flatten_target(item.optional_vars)

    for stmt in node.body:
        yield from get_bindings(stmt)


@get_bindings.register(ast.Raise)
def _get_bindings_for_raise(node):
    """
    ..code:: python


        Raise(expr? exc, expr? cause)
    """
    if node.cause is not None:
        yield from get_bindings(node.cause)

    if node.exc is not None:
        yield from get_bindings(node.exc)


@get_bindings.register(ast.Try)
def _get_bindings_for_try(node):
    """
    ..code:: python

        Try(
            stmt* body,
            excepthandler* handlers,
            stmt* orelse,
            stmt* finalbody,
        )

        ExceptHandler(expr? type, identifier? name, stmt* body)
    """

    for stmt in node.body:
        yield from get_bindings(stmt)

    for handler in node.handlers:
        if handler.name:
            yield handler.name

        for stmt in handler.body:
            yield from get_bindings(stmt)

    for stmt in node.orelse:
        yield from get_bindings(stmt)

    for stmt in node.finalbody:
        yield from get_bindings(stmt)


@get_bindings.register(ast.Assert)
def _get_bindings_for_assert(node):
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    yield from get_bindings(node.test)

    if node.msg is not None:
        yield from get_bindings(node.msg)


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
    for name in node.names:
        yield name


@get_bindings.register(ast.Nonlocal)
def _get_bindings_for_non_local(node):
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    for name in node.names:
        yield name


@get_bindings.register(ast.Expr)
def _get_bindings_for_expr(node):
    """
    ..code:: python

        Expr(expr value)
    """
    yield from get_bindings(node.value)


@get_bindings.register(ast.Pass)
@get_bindings.register(ast.Break)
@get_bindings.register(ast.Continue)
def _get_bindings_for_control_flow(node):
    """
    ..code:: python

        Pass | Break | Continue

    """
    return
    yield


@get_bindings.register(ast.NamedExpr)
def _get_bindings_for_named_expr(node):
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    yield from get_bindings(node.value)
    yield from _flatten_target(node.target)


@get_bindings.register(ast.BoolOp)
def _get_bindings_for_bool_op(node):
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    for expr in node.values:
        yield from get_bindings(expr)


@get_bindings.register(ast.BinOp)
def _get_bindings_for_bin_op(node):

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    yield from get_bindings(node.left)
    yield from get_bindings(node.right)


@get_bindings.register(ast.UnaryOp)
def _get_bindings_for_unary_op(node):
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """
    yield from get_bindings(node.operand)


@get_bindings.register(ast.Lambda)
def _get_bindings_for_lambda(node):
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    yield from _get_bindings_from_arguments(node.args)


@get_bindings.register(ast.IfExp)
def _get_bindings_for_if_exp(node):
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    yield from get_bindings(node.test)
    yield from get_bindings(node.body)
    yield from get_bindings(node.orelse)


@get_bindings.register(ast.Dict)
def _get_bindings_for_dict(node):
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    for key, value in zip(node.keys, node.values):
        if key is not None:
            yield from get_bindings(key)
        if value is not None:
            yield from get_bindings(value)


@get_bindings.register(ast.Set)
def _get_bindings_for_set(node):
    """
    ..code:: python

        Set(expr* elts)
    """
    for elt in node.elts:
        yield from get_bindings(elt)


@get_bindings.register(ast.ListComp)
def _get_bindings_for_list_comp(node):
    """
    ..code:: python

        comprehension = (expr target, expr iter, expr* ifs, int is_async)
        ListComp(expr elt, comprehension* generators)
    """
    for generator in node.generators:
        yield from get_bindings(generator.iter)
        yield from _flatten_target(generator.target)
        for condition in generator.ifs:
            yield from get_bindings(condition)

    yield from get_bindings(node.elt)


@get_bindings.register(ast.SetComp)
def _get_bindings_for_set_comp(node):
    """
    ..code:: python

        comprehension = (expr target, expr iter, expr* ifs, int is_async)
        SetComp(expr elt, comprehension* generators)
    """
    for generator in node.generators:
        yield from get_bindings(generator.iter)
        yield from _flatten_target(generator.target)
        for condition in generator.ifs:
            yield from get_bindings(condition)

    yield from get_bindings(node.elt)


@get_bindings.register(ast.DictComp)
def _get_bindings_for_dict_comp(node):
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    for generator in node.generators:
        yield from get_bindings(generator.iter)
        yield from _flatten_target(generator.target)
        for condition in generator.ifs:
            yield from get_bindings(condition)

    yield from get_bindings(node.key)
    yield from get_bindings(node.value)


@get_bindings.register(ast.GeneratorExp)
def _get_bindings_for_generator_exp(node):
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    for generator in node.generators:
        yield from get_bindings(generator.iter)
        yield from _flatten_target(generator.target)
        for condition in generator.ifs:
            yield from get_bindings(condition)

    yield from get_bindings(node.elt)


@get_bindings.register(ast.Await)
def _get_bindings_for_await(node):
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    yield from get_bindings(node.value)


@get_bindings.register(ast.Yield)
def _get_bindings_for_yield(node):
    """
    ..code:: python

        Yield(expr? value)
    """
    if node.value is not None:
        yield from get_bindings(node.value)


@get_bindings.register(ast.YieldFrom)
def _get_bindings_for_yield_from(node):
    """
    ..code:: python

        YieldFrom(expr value)
    """
    yield from get_bindings(node.value)


@get_bindings.register(ast.Compare)
def _get_bindings_for_compare(node):
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    yield from get_bindings(node.left)
    for comparator in node.comparators:
        yield from get_bindings(comparator)


@get_bindings.register(ast.Call)
def _get_bindings_for_call(node):
    """
    ..code:: python

        keyword = (identifier? arg, expr value)
        Call(expr func, expr* args, keyword* keywords)
    """
    yield from get_bindings(node.func)

    for arg in node.args:
        yield from get_bindings(arg)

    for kwarg in node.keywords:
        yield from get_bindings(kwarg.value)


@get_bindings.register(ast.FormattedValue)
def _get_bindings_for_formatted_value(node):
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    yield from get_bindings(node.value)


@get_bindings.register(ast.JoinedStr)
def _get_bindings_for_joined_str(node):
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    for value in node.values:
        yield from get_bindings(value)


@get_bindings.register(ast.Constant)
def _get_bindings_for_constant(node):
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    return
    yield


@get_bindings.register(ast.Attribute)
def _get_bindings_for_attribute(node):
    """
    ..code:: python

        Attribute(expr value, identifier attr, expr_context ctx)
    """
    yield from get_bindings(node.value)


@get_bindings.register(ast.Slice)
def _get_bindings_for_slice(node):
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    if node.lower is not None:
        yield from get_bindings(node.lower)

    if node.upper is not None:
        yield from get_bindings(node.upper)

    if node.step is not None:
        yield from get_bindings(node.step)


if sys.version_info < (3, 9):

    @get_bindings.register(ast.Index)
    def _get_bindings_for_index(node):
        """
        ..code:: python

            # can appear only in Subscript
            Index(expr value)
        """
        yield from get_bindings(node.value)


@get_bindings.register(ast.Subscript)
def _get_bindings_for_subscript(node):
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    yield from get_bindings(node.value)
    yield from get_bindings(node.slice)


@get_bindings.register(ast.Starred)
def _get_bindings_for_starred(node):
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """
    yield from get_bindings(node.value)


@get_bindings.register(ast.Name)
def _get_bindings_for_name(node):

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    return
    yield


@get_bindings.register(ast.List)
def _get_bindings_for_list(node):

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    for elt in node.elts:
        yield from get_bindings(elt)


@get_bindings.register(ast.Tuple)
def _get_bindings_for_tuple(node):
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    for elt in node.elts:
        yield from get_bindings(elt)
