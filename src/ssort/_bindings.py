import ast
import functools


@functools.singledispatch
def get_bindings(node):
    return []


@get_bindings.register(ast.FunctionDef)
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
    """
    return [node.name]


@get_bindings.register(ast.AsyncFunctionDef)
def _get_bindings_for_async_function_def(node):
    """
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
    return [node.name]


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
    return [node.name]


@get_bindings.register(ast.Return)
def _get_bindings_for_return(node):
    """
    ..code:: python

        Return(expr? value)

    """
    return []


@get_bindings.register(ast.Delete)
def _get_bindings_for_delete(node):
    """
    ..code:: python

        Delete(expr* targets)
    """
    return []


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
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    bindings = []
    for target in node.targets:
        bindings += _flatten_target(target)

    return bindings


@get_bindings.register(ast.AugAssign)
def _get_bindings_for_aug_assign(node):
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.AnnAssign)
def _get_bindings_for_ann_assign(node):
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.For)
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
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.AsyncFor)
def _get_bindings_for_async_for(node):
    """
    ..code:: python

        AsyncFor(
            expr target,
            expr iter,
            stmt* body,
            stmt* orelse,
            string? type_comment,
        )
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.While)
def _get_bindings_for_while(node):
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.If)
def _get_bindings_for_if(node):
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.With)
def _get_bindings_for_with(node):
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.AsyncWith)
def _get_bindings_for_async_with(node):
    """
    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Raise)
def _get_bindings_for_raise(node):
    """
    ..code:: python


        Raise(expr? exc, expr? cause)
    """
    raise NotImplementedError("TODO")


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
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Assert)
def _get_bindings_for_assert(node):
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Import)
def _get_bindings_for_import(node):
    """
    ..code:: python

        Import(alias* names)
    """
    return [name.asname if name.asname else name.name for name in node.names]


@get_bindings.register(ast.ImportFrom)
def _get_bindings_for_import_from(node):
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    return [name.asname if name.asname else name.name for name in node.names]


@get_bindings.register(ast.Global)
def _get_bindings_for_global(node):
    """
    ..code:: python

        Global(identifier* names)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Nonlocal)
def _get_bindings_for_non_local(node):
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Expr)
def _get_bindings_for_expr(node):
    """
    ..code:: python

        Expr(expr value)
    """
    return get_bindings(node.value)


@get_bindings.register(ast.Pass)
@get_bindings.register(ast.Break)
@get_bindings.register(ast.Continue)
def _get_bindings_for_control_flow(node):
    """
    ..code:: python

        Pass | Break | Continue

    """
    return []


@get_bindings.register(ast.BoolOp)
def _get_bindings_for_bool_op(node):
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.NamedExpr)
def _get_bindings_for_named_expr(node):
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.BinOp)
def _get_bindings_for_bin_op(node):

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.UnaryOp)
def _get_bindings_for_unary_op(node):
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """
    return []


@get_bindings.register(ast.Lambda)
def _get_bindings_for_lambda(node):
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    return []


@get_bindings.register(ast.IfExp)
def _get_bindings_for_if_exp(node):
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Dict)
def _get_bindings_for_dict(node):
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Set)
def _get_bindings_for_set(node):
    """
    ..code:: python

        Set(expr* elts)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.ListComp)
def _get_bindings_for_list_comp(node):
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.SetComp)
def _get_bindings_for_set_comp(node):
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.DictComp)
def _get_bindings_for_dict_comp(node):
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.GeneratorExp)
def _get_bindings_for_generator_exp(node):
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Await)
def _get_bindings_for_await(node):
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Yield)
def _get_bindings_for_yield(node):
    """
    ..code:: python

        Yield(expr? value)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.YieldFrom)
def _get_bindings_for_yield_from(node):
    """
    ..code:: python

        YieldFrom(expr value)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Compare)
def _get_bindings_for_compare(node):
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Call)
def _get_bindings_for_call(node):
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    return []


@get_bindings.register(ast.FormattedValue)
def _get_bindings_for_formatted_value(node):
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.JoinedStr)
def _get_bindings_for_joined_str(node):
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Constant)
def _get_bindings_for_constant(node):
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    return []


@get_bindings.register(ast.Attribute)
def _get_bindings_for_attribute(node):
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Subscript)
def _get_bindings_for_subscript(node):
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    raise NotImplementedError("TODO")


@get_bindings.register(ast.Starred)
def _get_bindings_for_starred(node):
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """

    return get_bindings(node.value)


@get_bindings.register(ast.Name)
def _get_bindings_for_name(node):

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    return []


@get_bindings.register(ast.List)
def _get_bindings_for_list(node):

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    return []


@get_bindings.register(ast.Tuple)
def _get_bindings_for_tuple(node):
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    return []


@get_bindings.register(ast.Slice)
def _get_bindings_for_slice(node):
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    return []