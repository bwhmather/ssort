import ast
import sys
import textwrap

import pytest

from ssort._requirements import get_requirements

match_statement = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="match statements were introduced in python 3.10",
)


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


def _dep_names(node):
    return [dep.name for dep in get_requirements(node)]


def test_function_def_requirements():
    node = _parse(
        """
        def function():
            name
        """
    )
    assert _dep_names(node) == ["name"]


def test_function_def_requirements_multiple():
    node = _parse(
        """
        def function():
            a
            b
        """
    )
    assert _dep_names(node) == ["a", "b"]


def test_function_def_requirements_arg_shadows():
    node = _parse(
        """
        def function(arg):
            arg
        """
    )
    assert _dep_names(node) == []


def test_function_def_requirements_positional_only_arg_shadows():
    node = _parse(
        """
        def function(arg, /):
            arg
        """
    )
    assert _dep_names(node) == []


def test_function_def_requirements_keyword_only_arg_shadows():
    node = _parse(
        """
        def function(*, arg):
            arg
        """
    )
    assert _dep_names(node) == []


def test_function_def_requirements_assignment_shadows():
    node = _parse(
        """
        def function():
            a = b
            a
        """
    )
    assert _dep_names(node) == ["b"]


def test_function_def_requirements_rest_shadows():
    node = _parse(
        """
        def function():
            _, *rest = value
            rest
        """
    )
    assert _dep_names(node) == ["value"]


def test_function_def_requirements_shadowed_after():
    node = _parse(
        """
        def function():
            a
            a = b
        """
    )
    assert _dep_names(node) == ["b"]


def test_function_def_requirements_decorator():
    node = _parse(
        """
        @decorator(arg)
        def function():
            pass
        """
    )
    assert _dep_names(node) == ["decorator", "arg"]


def test_function_def_requirements_nonlocal():
    node = _parse(
        """
        def function():
            nonlocal a
            a = 4
        """
    )
    assert _dep_names(node) == ["a"]


def test_function_def_requirements_nonlocal_closure():
    node = _parse(
        """
        def function():
            def inner():
                nonlocal a
                a = 4
            return inner
        """
    )
    assert _dep_names(node) == ["a"]


def test_function_def_requirements_nonlocal_closure_capture():
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
    assert _dep_names(node) == []


def test_function_def_requirements_global():
    node = _parse(
        """
        def function():
            global a
            a = 4
        """
    )
    assert _dep_names(node) == ["a"]


def test_function_def_requirements_global_closure():
    node = _parse(
        """
        def function():
            def inner():
                global a
                a = 4
            return inner
        """
    )
    assert _dep_names(node) == ["a"]


def test_function_def_requirements_global_closure_no_capture():
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
    assert _dep_names(node) == ["a"]


def test_function_def_requirements_default():
    node = _parse(
        """
        def function(a=b):
            pass
        """
    )
    assert _dep_names(node) == ["b"]


def test_function_def_requirements_annotations():
    node = _parse(
        """
        def function(a: b) -> c:
            pass
        """
    )
    assert _dep_names(node) == ["b", "c"]


def test_async_function_def_requirements():
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
    node = _parse(
        """
        async def function(arg):
            return await other(arg)
        """
    )
    assert _dep_names(node) == ["other"]


def test_class_def_requirements():
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
    assert _dep_names(node) == [
        "decorator",
        "arg",
        "B",
        "C",
        "something",
        "something",
        "method_decorator",
        "_b",
    ]


def test_class_def_builtin_requirements():
    node = _parse(
        """
        class A:
            name = __qualname__
            def method(self):
                return __module__
        """
    )
    assert _dep_names(node) == ["__module__"]


def test_return_requirements():
    """
    ..code:: python

        Return(expr? value)

    """
    node = _parse("return a + b")
    assert _dep_names(node) == ["a", "b"]


def test_delete_requirements():
    """
    ..code:: python

        Delete(expr* targets)
    """
    node = _parse("del something")
    assert _dep_names(node) == ["something"]


def test_delete_requirements_multiple():
    node = _parse("del a, b")
    assert _dep_names(node) == ["a", "b"]


def test_delete_requirements_tuple():
    node = _parse("del (a, b)")
    assert _dep_names(node) == ["a", "b"]


def test_delete_requirements_subscript():
    node = _parse("del a[b:c]")
    assert _dep_names(node) == ["a", "b", "c"]


def test_delete_requirements_attribute():
    node = _parse("del obj.attr")
    assert _dep_names(node) == ["obj"]


def test_delete_requirements_mixed():
    node = _parse("del (a[b:c], d.f)")
    assert _dep_names(node) == ["a", "b", "c", "d"]


def test_assign_requirements():
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    node = _parse("a = b")
    assert _dep_names(node) == ["b"]


def test_assign_attribute_requirements():
    node = _parse("a.b = c")
    assert _dep_names(node) == ["a", "c"]


def test_assign_star_requirements():
    node = _parse("*a = c")
    assert _dep_names(node) == ["c"]


def test_assign_star_attribute_requirements():
    node = _parse("*a.b = c")
    assert _dep_names(node) == ["a", "c"]


def test_assign_subscript_requirements():
    node = _parse("a[b] = c")
    assert _dep_names(node) == ["a", "b", "c"]


def test_assign_tuple_requirements():
    node = _parse("a, b[c], d.e, *f = g")
    assert _dep_names(node) == ["b", "c", "d", "g"]


def test_aug_assign_requirements():
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    node = _parse("a += b")
    assert _dep_names(node) == ["b"]


def test_aug_assign_requirements_attribute():
    node = _parse("a.b += c")
    assert _dep_names(node) == ["a", "c"]


def test_ann_assign_requirements():
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    node = _parse("a: b = c")
    assert _dep_names(node) == ["b", "c"]


def test_ann_assign_requirements_attribute():
    node = _parse("a.b: c = d")
    assert _dep_names(node) == ["a", "c", "d"]


def test_for_requirements():
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
    node = _parse(
        """
        for a in b(c):
            d = a + e
        else:
            f = g
        """
    )
    assert _dep_names(node) == ["b", "c", "e", "g"]


def test_for_requirements_target_replaces_scope():
    node = _parse(
        """
        for a in a():
            pass
        """
    )
    assert _dep_names(node) == ["a"]


def test_for_requirements_attribute():
    node = _parse(
        """
        for a.b in c:
            pass
        """
    )
    assert _dep_names(node) == ["a", "c"]


def test_async_for_requirements():
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
    node = _parse(
        """
        for a in b(c):
            d = a + e
        else:
            f = g
        """
    )
    assert _dep_names(node) == ["b", "c", "e", "g"]


def test_while_requirements():
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    node = _parse(
        """
        while predicate():
            action()
        else:
            cleanup()
        """
    )
    assert _dep_names(node) == ["predicate", "action", "cleanup"]


def test_if_requirements():
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    node = _parse(
        """
        if predicate():
            return subsequent()
        else:
            return alternate()
        """
    )
    assert _dep_names(node) == ["predicate", "subsequent", "alternate"]


def test_with_requirements():
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
    assert _dep_names(node) == ["A", "b"]


def test_with_requirements_shadow():
    node = _parse(
        """
        with a as a:
            pass
        """
    )
    assert _dep_names(node) == ["a"]


def test_with_requirements_attribute():
    node = _parse(
        """
        with a as b.c:
            pass
        """
    )
    assert _dep_names(node) == ["a", "b"]


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
    assert _dep_names(node) == [
        "chdir",
        "os",
        "path",
        "parse_requirements",
        "path",
        "results",
    ]


def test_async_with_requirements():
    """
    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    node = _parse(
        """
        async with A() as a:
            a()
            b()
        """
    )
    assert _dep_names(node) == ["A", "b"]


def test_raise_requirements():
    """
    ..code:: python

        Raise(expr? exc, expr? cause)
    """
    node = _parse("raise Exception(message)")
    assert _dep_names(node) == ["Exception", "message"]


def test_try_requirements():
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
    assert _dep_names(node) == [
        "something_stupid",
        "Exception",
        "recover",
        "otherwise",
        "finish",
    ]


def test_assert_requirements():
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    pass


def test_import_requirements():
    """
    ..code:: python

        Import(alias* names)
    """
    pass


def test_import_from_requirements():
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    pass


def test_global_requirements():
    """
    ..code:: python

        Global(identifier* names)
    """
    pass


def test_non_local_requirements():
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    pass


def test_expr_requirements():
    """
    ..code:: python

        Expr(expr value)
    """
    pass


def test_control_flow_requirements():
    """
    ..code:: python

        Pass | Break | Continue

    """
    return []


def test_bool_op_requirements():
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    pass


def test_named_expr_requirements():
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    node = _parse("(a := b)")
    assert _dep_names(node) == ["b"]


def test_bin_op_requirements():
    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    node = _parse("a + b")
    assert _dep_names(node) == ["a", "b"]


def test_unary_op_requirements():
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """
    node = _parse("-plus")
    assert _dep_names(node) == ["plus"]


def test_lambda_requirements():
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    node = _parse("lambda arg, *args, **kwargs: arg + other(*args) / kwargs")
    assert _dep_names(node) == ["other"]


def test_lambda_requirements_default():
    node = _parse("lambda a=b: a")
    assert _dep_names(node) == ["b"]


def test_lambda_requirements_walrus_operator():
    node = _parse("lambda: (a := 1) + a")
    assert _dep_names(node) == []


def test_if_exp_requirements():
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    pass


def test_dict_requirements():
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    node = _parse("{key: value}")
    assert _dep_names(node) == ["key", "value"]


def test_dict_requirements_empty():
    node = _parse("{}")
    assert _dep_names(node) == []


def test_dict_requirements_unpack():
    node = _parse("{**values}")
    assert _dep_names(node) == ["values"]


def test_set_requirements():
    """
    ..code:: python

        Set(expr* elts)
    """
    pass


def test_list_comp_requirements():
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    node = _parse("[action(a) for a in iterator]")
    assert _dep_names(node) == ["action", "iterator"]


def test_set_comp_requirements():
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    node = _parse("{action(a) for a in iterator}")
    assert _dep_names(node) == ["action", "iterator"]


def test_dict_comp_requirements():
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    node = _parse(
        """
        {
            process_key(key): process_value(value)
            for key, value in iterator
        }
        """
    )
    assert _dep_names(node) == ["process_key", "process_value", "iterator"]


def test_generator_exp_requirements():
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    pass


def test_await_requirements():
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    pass


def test_yield_requirements():
    """
    ..code:: python

        Yield(expr? value)
    """
    pass


def test_yield_from_requirements():
    """
    ..code:: python

        YieldFrom(expr value)
    """
    pass


def test_compare_requirements():
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    pass


def test_call_requirements():
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    node = _parse("function(1, arg_value, kwarg=kwarg_value, kwarg_2=2)")
    assert _dep_names(node) == [
        "function",
        "arg_value",
        "kwarg_value",
    ]


def test_call_requirements_arg_unpacking():
    node = _parse("function(*args)")
    assert _dep_names(node) == ["function", "args"]


def test_call_requirements_kwarg_unpacking():
    node = _parse("function(*kwargs)")
    assert _dep_names(node) == [
        "function",
        "kwargs",
    ]


def test_method_call_requirements():
    node = _parse("obj.method(arg_value, kwarg=kwarg_value)")
    assert _dep_names(node) == [
        "obj",
        "arg_value",
        "kwarg_value",
    ]


def test_formatted_value_requirements():
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    node = _parse("f'{a} {b} {c}'")
    assert _dep_names(node) == ["a", "b", "c"]


def test_formatted_value_requirements_format_spec():
    node = _parse("f'{a} {b:{c}} {d}'")
    assert _dep_names(node) == ["a", "b", "c", "d"]


def test_formatted_value_requirements_format_spec_walrus():
    node = _parse("f'{a} {b:{(c := 1)}} {d}'")
    assert _dep_names(node) == ["a", "b", "d"]


def test_joined_str_requirements():
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    pass


def test_constant_requirements():
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    pass


def test_attribute_requirements():
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    node = _parse("obj.attr.method()")
    assert _dep_names(node) == ["obj"]


def test_subscript_requirements():
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    node = _parse("array[key]")
    assert _dep_names(node) == ["array", "key"]


def test_subscript_requirements_slice():
    node = _parse("array[start:end]")
    assert _dep_names(node) == ["array", "start", "end"]


def test_subscript_requirements_slice_end():
    node = _parse("array[:end]")
    assert _dep_names(node) == ["array", "end"]


def test_subscript_requirements_slice_start():
    node = _parse("array[start:]")
    assert _dep_names(node) == ["array", "start"]


def test_subscript_requirements_slice_all():
    node = _parse("array[:]")
    assert _dep_names(node) == ["array"]


def test_starred_requirements():
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """

    pass


def test_name_requirements():
    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    node = _parse("name")
    assert _dep_names(node) == ["name"]


def test_list_requirements():
    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    pass


def test_tuple_requirements():
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    node = _parse("(a, b, 3)")
    assert _dep_names(node) == ["a", "b"]


def test_tuple_requirements_star_unpacking():
    node = _parse("(a, *b)")
    assert _dep_names(node) == ["a", "b"]


def test_slice_requirements():
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    pass


@match_statement
def test_match_statement_requirements_literal():
    node = _parse(
        """
        match a:
            case True:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_capture():
    node = _parse(
        """
        match a:
            case b:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_wildcard():
    node = _parse(
        """
        match a:
            case _:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_constant():
    node = _parse(
        """
        match a:
            case 1:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_named_constant():
    node = _parse(
        """
        match a:
            case MyEnum.CONSTANT:
                pass
        """
    )
    assert _dep_names(node) == ["a", "MyEnum"]


@match_statement
def test_match_statement_requirements_sequence():
    node = _parse(
        """
        match a:
            case [b, *c, d, _]:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_mapping():
    node = _parse(
        """
        match a:
            case {"k1": "v1", "k2": b, "k3": _, **c}:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_class():
    node = _parse(
        """
        match a:
            case MyClass(0, b, x=_, y=c):
                pass
        """
    )
    assert _dep_names(node) == ["a", "MyClass"]


@match_statement
def test_match_statement_requirements_or():
    node = _parse(
        """
        match a:
            case b | c:
                pass
        """
    )
    assert _dep_names(node) == ["a"]


@match_statement
def test_match_statement_requirements_as():
    node = _parse(
        """
        match a:
            case b as c:
                pass
        """
    )
    assert _dep_names(node) == ["a"]
