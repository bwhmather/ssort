import ast
import functools
import sys


@functools.singledispatch
def _get_attribute_accesses(node, variable):
    raise NotImplementedError(
        f"could not find requirements for unsupported node:  {node!r}"
        f"at line {node.lineno}, column: {node.col_offset}"
    )


@_get_attribute_accesses.register(ast.FunctionDef)
@_get_attribute_accesses.register(ast.AsyncFunctionDef)
def _get_attribute_accesses_for_function_def(node, variable):
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
    # TODO
    return
    yield


@_get_attribute_accesses.register(ast.ClassDef)
def _get_attribute_accesses_for_class_def(node, variable):
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
    # TODO
    return
    yield


@_get_attribute_accesses.register(ast.Return)
def _get_attribute_accesses_for_return(node, variable):
    """
    ..code:: python

        Return(expr? value)

    """
    if node.value:
        yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.Delete)
def _get_attribute_accesses_for_delete(node, variable):
    """
    ..code:: python

        Delete(expr* targets)
    """
    for target in node.targets:
        yield from _get_attribute_accesses(target, variable)


@_get_attribute_accesses.register(ast.Assign)
def _get_attribute_accesses_for_assign(node, variable):
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    for target in node.targets:
        yield from _get_attribute_accesses(target, variable)
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.AugAssign)
def _get_attribute_accesses_for_aug_assign(node, variable):
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    yield from _get_attribute_accesses(node.target, variable)
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.AnnAssign)
def _get_attribute_accesses_for_ann_assign(node, variable):
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    yield from _get_attribute_accesses(node.target, variable)

    # Can be None for type declaration.
    if node.value:
        yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.For)
@_get_attribute_accesses.register(ast.AsyncFor)
def _get_attribute_accesses_for_for(node, variable):
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
    # TODO handle shadowing.
    yield from _get_attribute_accesses(node.iter, variable)

    for stmt in node.body:
        yield from _get_attribute_accesses(stmt, variable)

    for stmt in node.orelse:
        yield from _get_attribute_accesses(stmt, variable)


@_get_attribute_accesses.register(ast.While)
def _get_attribute_accesses_for_while(node, variable):
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    # TODO handle shadowing.
    yield from _get_attribute_accesses(node.test, variable)

    for stmt in node.body:
        yield from _get_attribute_accesses(stmt, variable)

    for stmt in node.orelse:
        yield from _get_attribute_accesses(stmt, variable)


@_get_attribute_accesses.register(ast.If)
def _get_attribute_accesses_for_if(node, variable):
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    # TODO handle shadowing.
    yield from _get_attribute_accesses(node.test, variable)

    for stmt in node.body:
        yield from _get_attribute_accesses(stmt, variable)

    for stmt in node.orelse:
        yield from _get_attribute_accesses(stmt, variable)


@_get_attribute_accesses.register(ast.With)
@_get_attribute_accesses.register(ast.AsyncWith)
def _get_attribute_accesses_for_with(node, variable):
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)

    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)

    .. code:: python

        WithItem(expr context_expr, expr? optional_vars)
    """
    # TODO handle shadowing.
    for item in node.items:
        yield from _get_attribute_accesses(item.context_expr, variable)

    for stmt in node.body:
        yield from _get_attribute_accesses(stmt, variable)


@_get_attribute_accesses.register(ast.Raise)
def _get_attribute_accesses_for_raise(node, variable):
    """
    ..code:: python

        Raise(expr? exc, expr? cause)
    """
    if node.exc:
        yield from _get_attribute_accesses(node.exc, variable)

    if node.cause:
        yield from _get_attribute_accesses(node.cause, variable)


@_get_attribute_accesses.register(ast.Try)
def _get_attribute_accesses_for_try(node, variable):
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
    # TODO handle shadowing.
    for stmt in node.body:
        yield from _get_attribute_accesses(stmt, variable)

    for handler in node.handlers:
        if handler.type:
            yield from _get_attribute_accesses(handler.type, variable)

        for stmt in handler.body:
            yield from _get_attribute_accesses(stmt, variable)

    for stmt in node.orelse:
        yield from _get_attribute_accesses(stmt, variable)

    for stmt in node.finalbody:
        yield from _get_attribute_accesses(stmt, variable)


@_get_attribute_accesses.register(ast.Assert)
def _get_attribute_accesses_for_assert(node, variable):
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    yield from _get_attribute_accesses(node.test, variable)

    if node.msg:
        yield from _get_attribute_accesses(node.msg, variable)


@_get_attribute_accesses.register(ast.Import)
def _get_attribute_accesses_for_import(node, variable):
    """
    ..code:: python

        Import(alias* names)
    """
    return
    yield


@_get_attribute_accesses.register(ast.ImportFrom)
def _get_attribute_accesses_for_import_from(node, variable):
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    return
    yield


@_get_attribute_accesses.register(ast.Global)
def _get_attribute_accesses_for_global(node, variable):
    """
    ..code:: python

        Global(identifier* names)
    """
    return
    yield


@_get_attribute_accesses.register(ast.Nonlocal)
def _get_attribute_accesses_for_non_local(node, variable):
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    return
    yield


@_get_attribute_accesses.register(ast.Expr)
def _get_attribute_accesses_for_expr(node, variable):
    """
    ..code:: python

        Expr(expr value)
    """
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.Pass)
@_get_attribute_accesses.register(ast.Break)
@_get_attribute_accesses.register(ast.Continue)
def _get_attribute_accesses_for_control_flow(node, variable):
    """
    ..code:: python

        Pass | Break | Continue

    """
    return
    yield


@_get_attribute_accesses.register(ast.BoolOp)
def _get_attribute_accesses_for_bool_op(node, variable):
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    for value in node.values:
        yield from _get_attribute_accesses(value, variable)


@_get_attribute_accesses.register(ast.NamedExpr)
def _get_attribute_accesses_for_named_expr(node, variable):
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    raise NotImplementedError("TODO")


@_get_attribute_accesses.register(ast.BinOp)
def _get_attribute_accesses_for_bin_op(node, variable):

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    yield from _get_attribute_accesses(node.left, variable)
    yield from _get_attribute_accesses(node.right, variable)


@_get_attribute_accesses.register(ast.UnaryOp)
def _get_attribute_accesses_for_unary_op(node, variable):
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """

    yield from _get_attribute_accesses(node.operand, variable)


@_get_attribute_accesses.register(ast.Lambda)
def _get_attribute_accesses_for_lambda(node, variable):
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    # TODO handle shadowing.
    yield from _get_attribute_accesses(node.body, variable)


@_get_attribute_accesses.register(ast.IfExp)
def _get_attribute_accesses_for_if_exp(node, variable):
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    yield from _get_attribute_accesses(node.test, variable)
    yield from _get_attribute_accesses(node.body, variable)
    yield from _get_attribute_accesses(node.orelse, variable)


@_get_attribute_accesses.register(ast.Dict)
def _get_attribute_accesses_for_dict(node, variable):
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    for key, value in zip(node.keys, node.values):
        if key is not None:
            yield from _get_attribute_accesses(key, variable)
        yield from _get_attribute_accesses(value, variable)


@_get_attribute_accesses.register(ast.Set)
def _get_attribute_accesses_for_set(node, variable):
    """
    ..code:: python

        Set(expr* elts)
    """
    for elt in node.elts:
        yield from _get_attribute_accesses(elt, variable)


@_get_attribute_accesses.register(ast.ListComp)
def _get_attribute_accesses_for_list_comp(node, variable):
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    # TODO handle shadowing.
    yield from _get_attribute_accesses(node.elt, variable)

    for generator in node.generators:
        yield from _get_attribute_accesses(generator.iter, variable)
        for if_expr in generator.ifs:
            yield from _get_attribute_accesses(if_expr, variable)


@_get_attribute_accesses.register(ast.SetComp)
def _get_attribute_accesses_for_set_comp(node, variable):
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    yield from _get_attribute_accesses(node.elt, variable)

    for generator in node.generators:
        yield from _get_attribute_accesses(generator.iter, variable)
        for if_expr in generator.ifs:
            yield from _get_attribute_accesses(if_expr, variable)


@_get_attribute_accesses.register(ast.DictComp)
def _get_attribute_accesses_for_dict_comp(node, variable):
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    yield from _get_attribute_accesses(node.key, variable)
    yield from _get_attribute_accesses(node.value, variable)

    for generator in node.generators:
        yield from _get_attribute_accesses(generator.iter, variable)
        for if_expr in generator.ifs:
            yield from _get_attribute_accesses(if_expr, variable)


@_get_attribute_accesses.register(ast.GeneratorExp)
def _get_attribute_accesses_for_generator_exp(node, variable):
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    yield from _get_attribute_accesses(node.elt, variable)

    for generator in node.generators:
        yield from _get_attribute_accesses(generator.iter, variable)
        for if_expr in generator.ifs:
            yield from _get_attribute_accesses(if_expr, variable)


@_get_attribute_accesses.register(ast.Await)
def _get_attribute_accesses_for_await(node, variable):
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.Yield)
def _get_attribute_accesses_for_yield(node, variable):
    """
    ..code:: python

        Yield(expr? value)
    """
    if node.value:
        yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.YieldFrom)
def _get_attribute_accesses_for_yield_from(node, variable):
    """
    ..code:: python

        YieldFrom(expr value)
    """
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.Compare)
def _get_attribute_accesses_for_compare(node, variable):
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    yield from _get_attribute_accesses(node.left, variable)

    for comp in node.comparators:
        yield from _get_attribute_accesses(comp, variable)


@_get_attribute_accesses.register(ast.Call)
def _get_attribute_accesses_for_call(node, variable):
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    yield from _get_attribute_accesses(node.func, variable)

    for arg in node.args:
        yield from _get_attribute_accesses(arg, variable)

    for kwarg in node.keywords:
        yield from _get_attribute_accesses(kwarg.value, variable)


@_get_attribute_accesses.register(ast.FormattedValue)
def _get_attribute_accesses_for_formatted_value(node, variable):
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.JoinedStr)
def _get_attribute_accesses_for_joined_str(node, variable):
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    return
    yield


@_get_attribute_accesses.register(ast.Constant)
def _get_attribute_accesses_for_constant(node, variable):
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    return
    yield


@_get_attribute_accesses.register(ast.Attribute)
def _get_attribute_accesses_for_attribute(node, variable):
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    yield from _get_attribute_accesses(node.value, variable)
    if isinstance(node.value, ast.Name) and node.value.id == variable:
        yield node.attr


@_get_attribute_accesses.register(ast.Subscript)
def _get_attribute_accesses_for_subscript(node, variable):
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    yield from _get_attribute_accesses(node.value, variable)
    yield from _get_attribute_accesses(node.slice, variable)


@_get_attribute_accesses.register(ast.Starred)
def _get_attribute_accesses_for_starred(node, variable):
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """
    assert isinstance(node.ctx, ast.Load)
    yield from _get_attribute_accesses(node.value, variable)


@_get_attribute_accesses.register(ast.Name)
def _get_attribute_accesses_for_name(node, variable):

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    return
    yield


@_get_attribute_accesses.register(ast.List)
def _get_attribute_accesses_for_list(node, variable):

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    for element in node.elts:
        yield from _get_attribute_accesses(element, variable)


@_get_attribute_accesses.register(ast.Tuple)
def _get_attribute_accesses_for_tuple(node, variable):
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    for element in node.elts:
        yield from _get_attribute_accesses(element, variable)


@_get_attribute_accesses.register(ast.Slice)
def _get_attribute_accesses_for_slice(node, variable):
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    if node.lower is not None:
        yield from _get_attribute_accesses(node.lower, variable)

    if node.upper is not None:
        yield from _get_attribute_accesses(node.upper, variable)

    if node.step is not None:
        yield from _get_attribute_accesses(node.step, variable)


if sys.version_info < (3, 9):

    @_get_attribute_accesses.register(ast.Index)
    def _get_attribute_accesses_for_index(node, variable):
        """
        ..code:: python

            # can appear only in Subscript
            Index(expr value)
        """
        yield from _get_attribute_accesses(node.value, variable)


@functools.singledispatch
def get_method_requirements(node):
    return
    yield


@get_method_requirements.register(ast.FunctionDef)
@get_method_requirements.register(ast.AsyncFunctionDef)
def _get_method_requirements_for_function_def(node):
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
    if not node.args.args:
        return

    self_arg = node.args.args[0].arg

    for statement in node.body:
        yield from _get_attribute_accesses(statement, self_arg)
