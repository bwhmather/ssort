import ast
import functools

from ssort._bindings import get_bindings


@functools.singledispatch
def get_dependencies(node):
    return []


@get_dependencies.register(ast.FunctionDef)
def _get_dependencies_for_function_def(node):
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

    return [
        dependency for dependency in dependencies if dependency not in scope
    ]


@get_dependencies.register(ast.AsyncFunctionDef)
def _get_dependencies_for_async_function_def(node):
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
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.ClassDef)
def _get_dependencies_for_class_def(node):
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
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Return)
def _get_dependencies_for_return(node):
    """
    ..code:: python

        Return(expr? value)

    """
    return get_dependencies(node.value)


@get_dependencies.register(ast.Delete)
def _get_dependencies_for_delete(node):
    """
    ..code:: python

        Delete(expr* targets)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Assign)
def _get_dependencies_for_assign(node):
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    return get_dependencies(node.value)


@get_dependencies.register(ast.AugAssign)
def _get_dependencies_for_aug_assign(node):
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.AnnAssign)
def _get_dependencies_for_ann_assign(node):
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.For)
def _get_dependencies_for_for(node):
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


@get_dependencies.register(ast.AsyncFor)
def _get_dependencies_for_async_for(node):
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


@get_dependencies.register(ast.While)
def _get_dependencies_for_while(node):
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.If)
def _get_dependencies_for_if(node):
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.With)
def _get_dependencies_for_with(node):
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.AsyncWith)
def _get_dependencies_for_async_with(node):
    """
    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Raise)
def _get_dependencies_for_raise(node):
    """
    ..code:: python


        Raise(expr? exc, expr? cause)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Try)
def _get_dependencies_for_try(node):
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


@get_dependencies.register(ast.Assert)
def _get_dependencies_for_assert(node):
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Import)
def _get_dependencies_for_import(node):
    """
    ..code:: python

        Import(alias* names)
    """
    return []


@get_dependencies.register(ast.ImportFrom)
def _get_dependencies_for_import_from(node):
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    return []


@get_dependencies.register(ast.Global)
def _get_dependencies_for_global(node):
    """
    ..code:: python

        Global(identifier* names)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Nonlocal)
def _get_dependencies_for_non_local(node):
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Expr)
def _get_dependencies_for_expr(node):
    """
    ..code:: python

        Expr(expr value)
    """
    return get_dependencies(node.value)


@get_dependencies.register(ast.Pass)
@get_dependencies.register(ast.Break)
@get_dependencies.register(ast.Continue)
def _get_dependencies_for_control_flow(node):
    """
    ..code:: python

        Pass | Break | Continue

    """
    return []


@get_dependencies.register(ast.BoolOp)
def _get_dependencies_for_bool_op(node):
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.NamedExpr)
def _get_dependencies_for_named_expr(node):
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.BinOp)
def _get_dependencies_for_bin_op(node):

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    return [
        *get_dependencies(node.left),
        *get_dependencies(node.right),
    ]


@get_dependencies.register(ast.UnaryOp)
def _get_dependencies_for_unary_op(node):
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """

    return get_dependencies(node.operand)


@get_dependencies.register(ast.Lambda)
def _get_dependencies_for_lambda(node):
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.IfExp)
def _get_dependencies_for_if_exp(node):
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Dict)
def _get_dependencies_for_dict(node):
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Set)
def _get_dependencies_for_set(node):
    """
    ..code:: python

        Set(expr* elts)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.ListComp)
def _get_dependencies_for_list_comp(node):
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.SetComp)
def _get_dependencies_for_set_comp(node):
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.DictComp)
def _get_dependencies_for_dict_comp(node):
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.GeneratorExp)
def _get_dependencies_for_generator_exp(node):
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Await)
def _get_dependencies_for_await(node):
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Yield)
def _get_dependencies_for_yield(node):
    """
    ..code:: python

        Yield(expr? value)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.YieldFrom)
def _get_dependencies_for_yield_from(node):
    """
    ..code:: python

        YieldFrom(expr value)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Compare)
def _get_dependencies_for_compare(node):
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Call)
def _get_dependencies_for_call(node):
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    dependencies = get_dependencies(node.func)

    for arg in node.args:
        dependencies += get_dependencies(arg)

    for kwarg in node.keywords:
        dependencies += get_dependencies(kwarg.value)

    return dependencies


@get_dependencies.register(ast.FormattedValue)
def _get_dependencies_for_formatted_value(node):
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.JoinedStr)
def _get_dependencies_for_joined_str(node):
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Constant)
def _get_dependencies_for_constant(node):
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    return []


@get_dependencies.register(ast.Attribute)
def _get_dependencies_for_attribute(node):
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    return get_dependencies(node.value)


@get_dependencies.register(ast.Subscript)
def _get_dependencies_for_subscript(node):
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Starred)
def _get_dependencies_for_starred(node):
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """

    return get_dependencies(node.value)


@get_dependencies.register(ast.Name)
def _get_dependencies_for_name(node):

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    assert isinstance(node.ctx, ast.Load)
    return [node.id]


@get_dependencies.register(ast.List)
def _get_dependencies_for_list(node):

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    raise NotImplementedError("TODO")


@get_dependencies.register(ast.Tuple)
def _get_dependencies_for_tuple(node):
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    dependencies = []
    for element in node.elts:
        dependencies += get_dependencies(element)
    return dependencies


@get_dependencies.register(ast.Slice)
def _get_dependencies_for_slice(node):
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    raise NotImplementedError("TODO")