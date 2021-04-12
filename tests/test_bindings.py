import ast
import sys
import textwrap

from ssort._bindings import get_bindings


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


def test_function_def_bindings():
    node = _parse(
        """
        def function():
            name
        """
    )
    assert list(get_bindings(node)) == ["function"]


def test_async_function_def_bindings():
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


def test_class_def_bindings():
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
    pass


def test_return_bindings():
    """
    ..code:: python

        Return(expr? value)

    """
    pass


def test_delete_bindings():
    """
    ..code:: python

        Delete(expr* targets)
    """
    node = _parse("del something")
    assert list(get_bindings(node)) == []


def test_delete_bindings_multiple():
    node = _parse("del a, b")
    assert list(get_bindings(node)) == []


def test_delete_bindings_subscript():
    node = _parse("del a[b:c]")
    assert list(get_bindings(node)) == []


def test_delete_bindings_attribute():
    node = _parse("del obj.attr")
    assert list(get_bindings(node)) == []


def test_assign_bindings():
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    node = _parse("a = b")
    assert list(get_bindings(node)) == ["a"]


def test_assign_bindings_star():
    node = _parse("a, *b = c")
    assert list(get_bindings(node)) == ["a", "b"]


def test_assign_bindings_attribute():
    node = _parse("obj.attr = value")
    assert list(get_bindings(node)) == []


def test_assign_bindings_list():
    node = _parse("[a, b, [c, d]] = value")
    assert list(get_bindings(node)) == ["a", "b", "c", "d"]


def test_assign_bindings_list_star():
    node = _parse("[first, *rest] = value")
    assert list(get_bindings(node)) == ["first", "rest"]


def test_aug_assign_bindings():
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    node = _parse("a += b")
    assert list(get_bindings(node)) == ["a"]


def test_ann_assign_bindings():
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    node = _parse("a: int = b")
    assert list(get_bindings(node)) == ["a"]


def test_for_bindings():
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


def test_async_for_bindings():
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


def test_while_bindings():
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    pass


def test_if_bindings():
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    pass


def test_with_bindings():
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)
    """
    node = _parse(
        """
        with A() as a:
            a()
            b()
        """
    )
    assert list(get_bindings(node)) == ["a"]


def test_with_requirements_bindings():
    node = _parse(
        """
        with chdir(os.path.dirname(path)):
            requirements = parse_requirements(path)
            for req in requirements.values():
                if req.name:
                    results.append(req.name)
        """
    )
    assert list(get_bindings(node)) == ["requirements", "req"]


def test_async_with_bindings():
    """
    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    pass


def test_raise_bindings():
    """
    ..code:: python


        Raise(expr? exc, expr? cause)
    """
    pass


def test_try_bindings():
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
    assert list(get_bindings(node)) == ["a", "exc", "b", "c", "d"]


def test_assert_bindings():
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    pass


def test_import_bindings():
    """
    ..code:: python

        Import(alias* names)
    """
    node = _parse("import something")
    assert list(get_bindings(node)) == ["something"]


def test_import_bindings_as():
    node = _parse("import something as something_else")
    assert list(get_bindings(node)) == ["something_else"]


def test_import_bindings_nested():
    node = _parse("import module.submodule")
    assert list(get_bindings(node)) == ["module"]


def test_import_from_bindings():
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    node = _parse("from module import a, b")
    assert list(get_bindings(node)) == ["a", "b"]


def test_import_from_bindings_as():
    node = _parse("from module import something as something_else")
    assert list(get_bindings(node)) == ["something_else"]


def test_global_bindings():
    """
    ..code:: python

        Global(identifier* names)
    """
    pass


def test_non_local_bindings():
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    pass


def test_expr_bindings():
    """
    ..code:: python

        Expr(expr value)
    """
    pass


def test_control_flow_bindings():
    """
    ..code:: python

        Pass | Break | Continue

    """
    pass


def test_bool_op_bindings():
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    pass


def test_named_expr_bindings():
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    pass


def test_bin_op_bindings():

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    pass


def test_unary_op_bindings():
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """
    pass


def test_lambda_bindings():
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    pass


def test_if_exp_bindings():
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    pass


def test_dict_bindings():
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    node = _parse("{key: value}")
    assert list(get_bindings(node)) == []


def test_dict_bindings_empty():
    node = _parse("{}")
    assert list(get_bindings(node)) == []


def test_dict_bindings_unpack():
    node = _parse("{**values}")
    assert list(get_bindings(node)) == []


def test_set_bindings():
    """
    ..code:: python

        Set(expr* elts)
    """
    pass


def test_list_comp_bindings():
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    pass


def test_set_comp_bindings():
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    pass


def test_dict_comp_bindings():
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    pass


def test_generator_exp_bindings():
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    pass


def test_await_bindings():
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    pass


def test_yield_bindings():
    """
    ..code:: python

        Yield(expr? value)
    """
    pass


def test_yield_from_bindings():
    """
    ..code:: python

        YieldFrom(expr value)
    """
    pass


def test_compare_bindings():
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    pass


def test_call_bindings():
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    pass


def test_formatted_value_bindings():
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    pass


def test_joined_str_bindings():
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    pass


def test_constant_bindings():
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    pass


def test_attribute_bindings():
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    pass


def test_subscript_bindings():
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    pass


def test_starred_bindings():
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """

    pass


def test_name_bindings():

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    node = _parse("a")
    assert list(get_bindings(node)) == []


def test_list_bindings():

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    pass


def test_tuple_bindings():
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    pass


def test_slice_bindings():
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    pass
