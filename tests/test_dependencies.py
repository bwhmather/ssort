import ast
import sys
import textwrap

from ssort._dependencies import get_dependencies


def _parse(source):
    source = textwrap.dedent(source)
    root = ast.parse(source)
    assert len(root.body) == 1
    node = root.body[0]
    if sys.version_info >= (3, 9):
        print(ast.dump(node, include_attributes=True, indent=2))
    else:
        print(ast.dump(node, include_attributes=True))
    return node


def test_function_def_dependencies():
    node = _parse(
        """
        def function():
            name
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["name"]


def test_function_def_dependencies_multiple():
    node = _parse(
        """
        def function():
            a
            b
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["a", "b"]


def test_function_def_dependencies_arg_shadows():
    node = _parse(
        """
        def function(arg):
            arg
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == []


def test_function_def_dependencies_assignment_shadows():
    node = _parse(
        """
        def function():
            a = b
            a
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["b"]


def test_function_def_dependencies_rest_shadows():
    node = _parse(
        """
        def function():
            _, *rest = value
            rest
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["value"]


def test_function_def_dependencies_shadowed_after():
    node = _parse(
        """
        def function():
            a
            a = b
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["b"]


def test_function_def_dependencies_decorator():
    node = _parse(
        """
        @decorator(arg)
        def function():
            pass
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["decorator", "arg"]


def test_function_def_dependencies_nonlocal():
    node = _parse(
        """
        def function():
            nonlocal a
            a = 4
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["a"]


def test_function_def_dependencies_nonlocal_closure():
    node = _parse(
        """
        def function():
            def inner():
                nonlocal a
                a = 4
            return inner
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["a"]


def test_function_def_dependencies_nonlocal_closure_capture():
    node = _parse(
        """
        def function():
            def inner():
                nonlocal a
                a = 4
            a = 2
            return inner
        """
    )

    assert [dep.name for dep in get_dependencies(node)] == []


def test_function_def_dependencies_global():
    node = _parse(
        """
        def function():
            global a
            a = 4
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["a"]


def test_function_def_dependencies_global_closure():
    node = _parse(
        """
        def function():
            def inner():
                global a
                a = 4
            return inner
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == ["a"]


def test_function_def_dependencies_global_closure_no_capture():
    node = _parse(
        """
        def function():
            def inner():
                global a
                a = 4
            a = 2
            return inner
        """
    )

    assert [dep.name for dep in get_dependencies(node)] == ["a"]


def test_async_function_def_dependencies():
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
    pass


def test_class_def_dependencies():
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
    node = _parse(
        """
        @decorator(arg)
        class A(B, C):
            _a = something
            _b = something

            @method_decorator(_a)
            def method():
                return _b
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == [
        "decorator",
        "arg",
        "B",
        "C",
        "something",
        "something",
        "method_decorator",
        "_b",
    ]


def test_return_dependencies():
    """
    ..code:: python

        Return(expr? value)

    """
    pass


def test_delete_dependencies():
    """
    ..code:: python

        Delete(expr* targets)
    """
    pass


def test_assign_dependencies():
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    node = _parse("a = b")
    assert [dep.name for dep in get_dependencies(node)] == ["b"]


def test_aug_assign_dependencies():
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    node = _parse("a += b")
    assert [dep.name for dep in get_dependencies(node)] == ["b"]


def test_ann_assign_dependencies():
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    node = _parse("a: int = b")
    assert [dep.name for dep in get_dependencies(node)] == ["b"]


def test_for_dependencies():
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
    pass


def test_async_for_dependencies():
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
    pass


def test_while_dependencies():
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    pass


def test_if_dependencies():
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    pass


def test_with_dependencies():
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)
    """
    pass


def test_async_with_dependencies():
    """
    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    pass


def test_raise_dependencies():
    """
    ..code:: python


        Raise(expr? exc, expr? cause)
    """
    pass


def test_try_dependencies():
    """
    ..code:: python

        Try(
            stmt* body,
            excepthandler* handlers,
            stmt* orelse,
            stmt* finalbody,
        )
    """
    node = _parse(
        """
        try:
            a = something_stupid()
        except Exception as exc:
            b = recover()
        else:
            c = otherwise()
        finally:
            d = finish()
        """
    )
    assert [dep.name for dep in get_dependencies(node)] == [
        "something_stupid",
        "Exception",
        "recover",
        "otherwise",
        "finish",
    ]


def test_assert_dependencies():
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    pass


def test_import_dependencies():
    """
    ..code:: python

        Import(alias* names)
    """
    pass


def test_import_from_dependencies():
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    pass


def test_global_dependencies():
    """
    ..code:: python

        Global(identifier* names)
    """
    pass


def test_non_local_dependencies():
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    pass


def test_expr_dependencies():
    """
    ..code:: python

        Expr(expr value)
    """
    pass


def test_control_flow_dependencies():
    """
    ..code:: python

        Pass | Break | Continue

    """
    return []


def test_bool_op_dependencies():
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    pass


def test_named_expr_dependencies():
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    pass


def test_bin_op_dependencies():

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    node = _parse("a + b")
    assert [dep.name for dep in get_dependencies(node)] == ["a", "b"]


def test_unary_op_dependencies():
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """
    node = _parse("-plus")
    assert [dep.name for dep in get_dependencies(node)] == ["plus"]


def test_lambda_dependencies():
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    pass


def test_if_exp_dependencies():
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    pass


def test_dict_dependencies():
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    pass


def test_set_dependencies():
    """
    ..code:: python

        Set(expr* elts)
    """
    pass


def test_list_comp_dependencies():
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    pass


def test_set_comp_dependencies():
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    pass


def test_dict_comp_dependencies():
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    pass


def test_generator_exp_dependencies():
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    pass


def test_await_dependencies():
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    pass


def test_yield_dependencies():
    """
    ..code:: python

        Yield(expr? value)
    """
    pass


def test_yield_from_dependencies():
    """
    ..code:: python

        YieldFrom(expr value)
    """
    pass


def test_compare_dependencies():
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    pass


def test_call_dependencies():
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    node = _parse("function(1, arg_value, kwarg=kwarg_value, kwarg_2=2)")
    assert [dep.name for dep in get_dependencies(node)] == [
        "function",
        "arg_value",
        "kwarg_value",
    ]


def test_call_dependencies_arg_unpacking():
    node = _parse("function(*args)")
    assert [dep.name for dep in get_dependencies(node)] == ["function", "args"]


def test_call_dependencies_kwarg_unpacking():
    node = _parse("function(*kwargs)")
    assert [dep.name for dep in get_dependencies(node)] == [
        "function",
        "kwargs",
    ]


def test_method_call_dependencies():
    node = _parse("obj.method(arg_value, kwarg=kwarg_value)")
    assert [dep.name for dep in get_dependencies(node)] == [
        "obj",
        "arg_value",
        "kwarg_value",
    ]


def test_formatted_value_dependencies():
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    pass


def test_joined_str_dependencies():
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    pass


def test_constant_dependencies():
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    pass


def test_attribute_dependencies():
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    pass


def test_subscript_dependencies():
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    pass


def test_starred_dependencies():
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """

    pass


def test_name_dependencies():

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    node = _parse("name")
    assert [dep.name for dep in get_dependencies(node)] == ["name"]


def test_list_dependencies():

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    pass


def test_tuple_dependencies():
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    node = _parse("(a, b, 3)")
    assert [dep.name for dep in get_dependencies(node)] == ["a", "b"]


def test_tuple_dependencies_star_unpacking():
    node = _parse("(a, *b)")
    assert [dep.name for dep in get_dependencies(node)] == ["a", "b"]


def test_slice_dependencies():
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    pass
