import ast
import sys
import textwrap

import pytest

from ssort._bindings import get_bindings

# Most walrus operator syntax is valid in 3.8. Only use this decorator for the
# rare cases where it is not.
walrus_operator = pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="some walrus operator syntax is not valid prior to python 3.9",
)


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


def test_function_def_bindings():
    node = _parse(
        """
        def function():
            name
        """
    )
    assert list(get_bindings(node)) == ["function"]


def test_function_def_bindings_walrus_default():
    node = _parse(
        """
        def function(a, b = (b_binding := 2)):
            pass
        """
    )
    assert list(get_bindings(node)) == ["function", "b_binding"]


def test_function_def_bindings_walrus_kw_default():
    node = _parse(
        """
        def function(*, kw1 = (kw1_binding := 1), kw2):
            pass
        """
    )
    assert list(get_bindings(node)) == ["function", "kw1_binding"]


def test_function_def_bindings_walrus_type():
    node = _parse(
        """
        def function(
            posonly: (posonly_type := int), / ,
            arg: (arg_type := int),
            *args: (args_type := int),
            kwarg: (kwarg_type := int),
            **kwargs: (kwargs_type := int)
        ) -> (return_type := int):
            pass
        """
    )
    assert list(get_bindings(node)) == [
        "function",
        "posonly_type",
        "arg_type",
        "args_type",
        "kwarg_type",
        "kwargs_type",
        "return_type",
    ]


@walrus_operator
def test_function_def_bindings_walrus_decorator():
    node = _parse(
        """
        @(p := property)
        def prop(self):
            pass
        """
    )
    assert list(get_bindings(node)) == ["p", "prop"]


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
    node = _parse(
        """
        async def function():
            name
        """
    )
    assert list(get_bindings(node)) == ["function"]


def test_async_function_def_bindings_walrus_kw_default():
    node = _parse(
        """
        async def function(*, kw1 = (kw1_binding := 1), kw2):
            pass
        """
    )
    assert list(get_bindings(node)) == ["function", "kw1_binding"]


def test_async_function_def_bindings_walrus_type():
    node = _parse(
        """
        async def function(
            posonly: (posonly_type := int), / ,
            arg: (arg_type := int),
            *args: (args_type := int),
            kwarg: (kwarg_type := int),
            **kwargs: (kwargs_type := int)
        ) -> (return_type := int):
            pass
        """
    )
    assert list(get_bindings(node)) == [
        "function",
        "posonly_type",
        "arg_type",
        "args_type",
        "kwarg_type",
        "kwargs_type",
        "return_type",
    ]


@walrus_operator
def test_async_function_def_bindings_walrus_decorator():
    node = _parse(
        """
        @(p := property)
        async def prop(self):
            pass
        """
    )
    assert list(get_bindings(node)) == ["p", "prop"]


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
    node = _parse(
        """
        @decorator
        class ClassName:
            a = 1
            def b(self):
                pass
        """
    )
    assert list(get_bindings(node)) == ["ClassName"]


@walrus_operator
def test_class_def_bindings_walrus_decorator():
    node = _parse(
        """
        @(d := decorator())
        class ClassName:
            pass
        """
    )
    assert list(get_bindings(node)) == ["d", "ClassName"]


def test_class_def_bindings_walrus_base():
    node = _parse(
        """
        class ClassName(BaseClass, (OtherBase := namedtuple())):
            pass
        """
    )
    assert list(get_bindings(node)) == ["OtherBase", "ClassName"]


def test_class_def_bindings_walrus_metaclass():
    node = _parse(
        """
        class Class(metaclass=(class_meta := MetaClass)):
            pass
        """
    )
    assert list(get_bindings(node)) == ["class_meta", "Class"]


def test_class_def_bindings_walrus_body():
    node = _parse(
        """
        class Class:
            a = (prop := 2)
        """
    )
    assert list(get_bindings(node)) == ["Class"]


def test_return_bindings():
    """
    ..code:: python

        Return(expr? value)

    """
    node = _parse("return x")
    assert list(get_bindings(node)) == []


def test_return_bindings_walrus():
    node = _parse("return (x := 1)")
    assert list(get_bindings(node)) == ["x"]


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


def test_assign_bindings_walrus_value():
    node = _parse("a = (b := c)")
    assert list(get_bindings(node)) == ["a", "b"]


def test_aug_assign_bindings():
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    node = _parse("a += b")
    assert list(get_bindings(node)) == ["a"]


def test_aug_assign_bindings_attribute():
    node = _parse("obj.attr /= value")
    assert list(get_bindings(node)) == []


def test_aug_assign_bindings_walrus_value():
    node = _parse("a ^= (b := c)")
    assert list(get_bindings(node)) == ["a", "b"]


def test_ann_assign_bindings():
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    node = _parse("a: int = b")
    assert list(get_bindings(node)) == ["a"]


def test_ann_assign_bindings_no_value():
    # TODO this expression doesn't technically bind `a`.
    node = _parse("a: int")
    assert list(get_bindings(node)) == ["a"]


def test_ann_assign_bindings_walrus_value():
    node = _parse("a: int = (b := c)")
    assert list(get_bindings(node)) == ["a", "b"]


def test_ann_assign_bindings_walrus_type():
    node = _parse("a: (a_type := int) = 4")
    assert list(get_bindings(node)) == ["a", "a_type"]


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
    node = _parse(
        """
        for i in range(10):
            a += i
        else:
            b = 4
        """
    )
    assert list(get_bindings(node)) == ["i", "a", "b"]


def test_for_bindings_walrus():
    node = _parse(
        """
        for i in (r := range(10)):
            pass
        """
    )
    assert list(get_bindings(node)) == ["i", "r"]


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
    node = _parse(
        """
        async for i in range(10):
            a += i
        else:
            b = 4
        """
    )
    assert list(get_bindings(node)) == ["i", "a", "b"]


def test_async_for_bindings_walrus():
    node = _parse(
        """
        async for i in (r := range(10)):
            pass
        """
    )
    assert list(get_bindings(node)) == ["i", "r"]


def test_while_bindings():
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    node = _parse(
        """
        while test():
            a = 1
        else:
            b = 2
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_while_bindings_walrus_test():
    node = _parse(
        """
        while (value := test):
            pass
        """
    )
    assert list(get_bindings(node)) == ["value"]


def test_if_bindings():
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    node = _parse(
        """
        if predicate_one():
            a = 1
        elif predicate_two():
            b = 2
        else:
            c = 3
        """
    )
    assert list(get_bindings(node)) == ["a", "b", "c"]


def test_if_bindings_walrus_test():
    node = _parse(
        """
        if (result := predicate()):
            pass
        """
    )
    assert list(get_bindings(node)) == ["result"]


def test_with_bindings():
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)
    """
    node = _parse(
        """
        with A() as a:
            b = 4
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_with_bindings_requirements_example():
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


def test_with_bindings_multiple():
    node = _parse(
        """
        with A() as a, B() as b:
            pass
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_with_bindings_unbound():
    node = _parse(
        """
        with A():
            pass
        """
    )
    assert list(get_bindings(node)) == []


def test_with_bindings_tuple():
    node = _parse(
        """
        with A() as (a, b):
            pass
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_with_bindings_walrus():
    node = _parse(
        """
        with (ctx := A()) as a:
            pass
        """
    )
    assert list(get_bindings(node)) == ["ctx", "a"]


def test_async_with_bindings():
    """
    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)
    """
    node = _parse(
        """
        async with A() as a:
            b = 4
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_async_with_bindings_multiple():
    node = _parse(
        """
        async with A() as a, B() as b:
            pass
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_async_with_bindings_unbound():
    node = _parse(
        """
        async with A():
            pass
        """
    )
    assert list(get_bindings(node)) == []


def test_async_with_bindings_tuple():
    node = _parse(
        """
        async with A() as (a, b):
            pass
        """
    )
    assert list(get_bindings(node)) == ["a", "b"]


def test_async_with_bindings_walrus():
    node = _parse(
        """
        async with (ctx := A()) as a:
            pass
        """
    )
    assert list(get_bindings(node)) == ["ctx", "a"]


def test_raise_bindings():
    """
    ..code:: python

        Raise(expr? exc, expr? cause)
    """
    node = _parse("raise TypeError()")
    assert list(get_bindings(node)) == []


def test_raise_bindings_reraise():
    node = _parse("raise")
    assert list(get_bindings(node)) == []


def test_raise_bindings_with_cause():
    node = _parse("raise TypeError() from exc")
    assert list(get_bindings(node)) == []


def test_raise_bindings_walrus():
    node = _parse("raise (exc := TypeError())")
    assert list(get_bindings(node)) == ["exc"]


def test_raise_bindings_walrus_in_cause():
    node = _parse("raise TypeError() from (original := exc)")
    assert list(get_bindings(node)) == ["original"]


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


def test_try_bindings_walrus():
    node = _parse(
        """
        try:
            pass
        except (x := Exception):
            pass
        """
    )
    assert list(get_bindings(node)) == ["x"]


def test_assert_bindings():
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    node = _parse("assert condition()")
    assert list(get_bindings(node)) == []


def test_assert_bindings_with_message():
    node = _parse('assert condition(), "message"')
    assert list(get_bindings(node)) == []


def test_assert_bindings_walrus_condition():
    node = _parse("assert (result := condition())")
    assert list(get_bindings(node)) == ["result"]


def test_assert_bindings_walrus_message():
    node = _parse('assert condition, (message := "message")')
    assert list(get_bindings(node)) == ["message"]


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
    node = _parse("global name")
    assert list(get_bindings(node)) == ["name"]


def test_global_bindings_multiple():
    node = _parse("global a, b")
    assert list(get_bindings(node)) == ["a", "b"]


def test_non_local_bindings():
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    node = _parse("nonlocal name")
    assert list(get_bindings(node)) == ["name"]


def test_nonlocal_bindings_multiple():
    node = _parse("nonlocal a, b")
    assert list(get_bindings(node)) == ["a", "b"]


def test_pass_bindings():
    """
    ..code:: python

        Pass

    """
    node = _parse("pass")
    assert list(get_bindings(node)) == []


def test_break_bindings():
    """
    ..code:: python

        Break

    """
    node = _parse("break")
    assert list(get_bindings(node)) == []


def test_continue_bindings():
    """
    ..code:: python

        Continue

    """
    node = _parse("continue")
    assert list(get_bindings(node)) == []


def test_bool_op_bindings():
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    node = _parse("a and b")
    assert list(get_bindings(node)) == []


def test_named_expr_bindings():
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    node = _parse("(a := b)")
    assert list(get_bindings(node)) == ["a"]


def test_named_expr_bindings_recursive():
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    node = _parse("(a := (b := (c := d)))")
    assert list(get_bindings(node)) == ["a", "b", "c"]


def test_bool_op_bindings_walrus_left():
    node = _parse("(left := a) and b")
    assert list(get_bindings(node)) == ["left"]


def test_bool_op_bindings_walrus_right():
    node = _parse("a or (right := b)")
    assert list(get_bindings(node)) == ["right"]


def test_bool_op_bindings_walrus_both():
    node = _parse("(left := a) and (right := b)")
    assert list(get_bindings(node)) == ["left", "right"]


def test_bool_op_bindings_walrus_multiple():
    node = _parse("(a := 1) and (b := 2) and (c := 3)")
    assert list(get_bindings(node)) == ["a", "b", "c"]


def test_bin_op_bindings():
    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    node = _parse("a and b")
    assert list(get_bindings(node)) == []


def test_bin_op_bindings_walrus_left():
    node = _parse("(left := a) | b")
    assert list(get_bindings(node)) == ["left"]


def test_bin_op_bindings_walrus_right():
    node = _parse("a ^ (right := b)")
    assert list(get_bindings(node)) == ["right"]


def test_bin_op_bindings_walrus_both():
    node = _parse("(left := a) + (right := b)")
    assert list(get_bindings(node)) == ["left", "right"]


def test_unary_op_bindings():
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """
    node = _parse("-a")
    assert list(get_bindings(node)) == []


def test_unary_op_bindings_walrus():
    node = _parse("-(a := b)")
    assert list(get_bindings(node)) == ["a"]


def test_lambda_bindings():
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    pass


def test_lambda_bindings_walrus_default():
    node = _parse("(lambda a, b = (b_binding := 2): None)")
    assert list(get_bindings(node)) == ["b_binding"]


def test_lambda_bindings_walrus_kw_default():
    node = _parse("(lambda *, kw1 = (kw1_binding := 1), kw2: None)")
    assert list(get_bindings(node)) == ["kw1_binding"]


def test_lambda_bindings_walrus_body():
    node = _parse("(lambda : (a := 1) + a)")
    assert list(get_bindings(node)) == []


def test_if_exp_bindings():
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    node = _parse("subsequent() if predicate() else alternate()")
    assert list(get_bindings(node)) == []


def test_if_exp_bindings_walrus_subsequent():
    node = _parse("(a := subsequent()) if predicate() else alternate()")
    assert list(get_bindings(node)) == ["a"]


def test_if_exp_bindings_walrus_predicate():
    node = _parse("subsequent() if (a := predicate()) else alternate()")
    assert list(get_bindings(node)) == ["a"]


def test_if_exp_bindings_walrus_alternate():
    node = _parse("subsequent() if predicate() else (a := alternate())")
    assert list(get_bindings(node)) == ["a"]


def test_if_exp_bindings_walrus():
    node = _parse(
        "(a := subsequent()) if (b := predicate()) else (c := alternate())"
    )
    assert list(get_bindings(node)) == ["b", "a", "c"]


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


def test_dict_bindings_walrus_key():
    node = _parse("{(key := genkey()): value}")
    assert list(get_bindings(node)) == ["key"]


def test_dict_bindings_walrus_value():
    node = _parse("{key: (value := genvalue())}")
    assert list(get_bindings(node)) == ["value"]


def test_dict_bindings_walrus_unpack():
    node = _parse("{key: value, **(rest := other)}")
    assert list(get_bindings(node)) == ["rest"]


def test_set_bindings():
    """
    ..code:: python

        Set(expr* elts)
    """
    node = _parse("{a, b, c}")
    assert list(get_bindings(node)) == []


def test_set_bindings_unpack():
    node = _parse("{a, b, *rest}")
    assert list(get_bindings(node)) == []


@walrus_operator
def test_set_bindings_walrus():
    node = _parse("{a, {b := genb()}, c}")
    assert list(get_bindings(node)) == ["b"]


def test_set_bindings_walrus_py38():
    node = _parse("{a, {(b := genb())}, c}")
    assert list(get_bindings(node)) == ["b"]


def test_set_bindings_walrus_unpack():
    node = _parse("{a, b, *(rest := other)}")
    assert list(get_bindings(node)) == ["rest"]


def test_list_comp_bindings():
    """
    ..code:: python

        comprehension = (expr target, expr iter, expr* ifs, int is_async)
        ListComp(expr elt, comprehension* generators)
    """
    node = _parse("[item for item in iterator if condition(item)]")
    assert list(get_bindings(node)) == ["item"]


def test_list_comp_bindings_walrus_target():
    node = _parse("[( a:= item) for item in iterator if condition(item)]")
    assert list(get_bindings(node)) == ["a", "item"]


def test_list_comp_bindings_walrus_iter():
    node = _parse("[item for item in (it := iterator) if condition(item)]")
    assert list(get_bindings(node)) == ["item", "it"]


def test_list_comp_bindings_walrus_condition():
    node = _parse("[item for item in iterator if (c := condition(item))]")
    assert list(get_bindings(node)) == ["item", "c"]


def test_set_comp_bindings():
    """
    ..code:: python

        comprehension = (expr target, expr iter, expr* ifs, int is_async)
        SetComp(expr elt, comprehension* generators)
    """
    node = _parse("{item for item in iterator if condition(item)}")
    assert list(get_bindings(node)) == ["item"]


def test_set_comp_bindings_walrus_target():
    node = _parse("{( a:= item) for item in iterator if condition(item)}")
    assert list(get_bindings(node)) == ["a", "item"]


def test_set_comp_bindings_walrus_iter():
    node = _parse("{item for item in (it := iterator) if condition(item)}")
    assert list(get_bindings(node)) == ["item", "it"]


def test_set_comp_bindings_walrus_condition():
    node = _parse("{item for item in iterator if (c := condition(item))}")
    assert list(get_bindings(node)) == ["item", "c"]


def test_dict_comp_bindings():
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    node = _parse("{item[0]: item[1] for item in iterator if check(item)}")
    assert list(get_bindings(node)) == ["item"]


def test_dict_comp_bindings_unpack():
    node = _parse("{key: value for key, value in iterator}")
    assert list(get_bindings(node)) == ["key", "value"]


def test_dict_comp_bindings_walrus_key():
    node = _parse(
        "{(key := item[0]): item[1] for item in iterator if check(item)}"
    )
    assert list(get_bindings(node)) == ["key", "item"]


def test_dict_comp_bindings_walrus_value():
    node = _parse(
        "{item[0]: (value := item[1]) for item in iterator if check(item)}"
    )
    assert list(get_bindings(node)) == ["value", "item"]


def test_dict_comp_bindings_walrus_iter():
    node = _parse(
        "{item[0]: item[1] for item in (it := iterator) if check(item)}"
    )
    assert list(get_bindings(node)) == ["item", "it"]


def test_dict_comp_bindings_walrus_condition():
    node = _parse(
        "{item[0]: item[1] for item in iterator if (c := check(item))}"
    )
    assert list(get_bindings(node)) == ["item", "c"]


def test_generator_exp_bindings():
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    node = _parse("(item for item in iterator if condition(item))")
    assert list(get_bindings(node)) == ["item"]


def test_generator_exp_bindings_walrus_target():
    node = _parse("(( a:= item) for item in iterator if condition(item))")
    assert list(get_bindings(node)) == ["a", "item"]


def test_generator_exp_bindings_walrus_iter():
    node = _parse("(item for item in (it := iterator) if condition(item))")
    assert list(get_bindings(node)) == ["item", "it"]


def test_generator_exp_bindings_walrus_condition():
    node = _parse("(item for item in iterator if (c := condition(item)))")
    assert list(get_bindings(node)) == ["item", "c"]


def test_await_bindings():
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    node = _parse("await fun()")
    assert list(get_bindings(node)) == []


def test_await_bindings_walrus():
    node = _parse("await (r := fun())")
    assert list(get_bindings(node)) == ["r"]


def test_yield_bindings():
    """
    ..code:: python

        Yield(expr? value)
    """
    node = _parse("yield fun()")
    assert list(get_bindings(node)) == []


def test_yield_bindings_no_result():
    node = _parse("yield")
    assert list(get_bindings(node)) == []


def test_yield_bindings_walrus():
    node = _parse("yield (r := fun())")
    assert list(get_bindings(node)) == ["r"]


def test_yield_from_bindings():
    """
    ..code:: python

        YieldFrom(expr value)
    """
    node = _parse("yield from fun()")
    assert list(get_bindings(node)) == []


def test_yield_from_bindings_walrus():
    node = _parse("yield from (r := fun())")
    assert list(get_bindings(node)) == ["r"]


def test_compare_bindings():
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    node = _parse("0 < value < 5")
    assert list(get_bindings(node)) == []


def test_compare_bindings_walrus():
    node = _parse("(a := 0) < (b := value) < (c := 5)")
    assert list(get_bindings(node)) == ["a", "b", "c"]


def test_call_bindings():
    """
    ..code:: python

        keyword = (identifier? arg, expr value)
        Call(expr func, expr* args, keyword* keywords)
    """
    node = _parse("fun(arg, *args, kwarg=kwarg, **kwargs)")
    assert list(get_bindings(node)) == []


def test_call_bindings_walrus_function():
    node = _parse("(f := fun)()")
    assert list(get_bindings(node)) == ["f"]


def test_call_bindings_walrus_args():
    node = _parse(
        """
        fun(
            (arg_binding := arg),
            *(args_binding := args),
            kwarg=(kwarg_binding := kwarg),
            **(kwargs_binding := kwargs),
        )
        """
    )
    assert list(get_bindings(node)) == [
        "arg_binding",
        "args_binding",
        "kwarg_binding",
        "kwargs_binding",
    ]


def test_joined_str_bindings():
    """
    ..code:: python

        JoinedStr(expr* values)
        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    node = _parse('f"a: {a}"')
    assert list(get_bindings(node)) == []


def test_joined_str_bindings_walrus():
    """
    ..code:: python

        JoinedStr(expr* values)
        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    node = _parse('f"a: {(a := get_a())}"')
    assert list(get_bindings(node)) == ["a"]


def test_constant_bindings():
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    node = _parse("1")
    assert list(get_bindings(node)) == []


def test_attribute_bindings():
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    node = _parse("a.b.c")
    assert list(get_bindings(node)) == []


def test_attribute_bindings_walrus():
    node = _parse("(a_binding := a).b")
    assert list(get_bindings(node)) == ["a_binding"]


def test_subscript_bindings():
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    node = _parse("a[b]")
    assert list(get_bindings(node)) == []


def test_subscript_bindings_slice():
    node = _parse("a[b:c]")
    assert list(get_bindings(node)) == []


def test_subscript_bindings_slice_with_step():
    node = _parse("a[b:c:d]")
    assert list(get_bindings(node)) == []


def test_subscript_bindings_walrus_value():
    node = _parse("(a_binding := a)[b]")
    assert list(get_bindings(node)) == ["a_binding"]


def test_subscript_bindings_walrus_index():
    node = _parse("a[(b_binding := b)]")
    assert list(get_bindings(node)) == ["b_binding"]


def test_subscript_bindings_walrus_slice():
    node = _parse("a[(b_binding := b):(c_binding := c)]")
    assert list(get_bindings(node)) == ["b_binding", "c_binding"]


def test_subscript_bindings_walrus_slice_with_step():
    node = _parse("a[(b_binding := b):(c_binding := c):(d_binding := d)]")
    assert list(get_bindings(node)) == ["b_binding", "c_binding", "d_binding"]


def test_starred_bindings():
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """
    node = _parse("*a")
    assert list(get_bindings(node)) == []


def test_starred_bindings_walrus():
    node = _parse("*(a_binding := a)")
    assert list(get_bindings(node)) == ["a_binding"]


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
    node = _parse("[a, b, c]")
    assert list(get_bindings(node)) == []


def test_list_bindings_unpack():
    node = _parse("{a, b, *rest}")
    assert list(get_bindings(node)) == []


def test_list_bindings_walrus():
    node = _parse("[a, (b := genb()), c]")
    assert list(get_bindings(node)) == ["b"]


def test_list_bindings_walrus_unpack():
    node = _parse("[a, b, *(rest := other)]")
    assert list(get_bindings(node)) == ["rest"]


def test_tuple_bindings():
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)
    """
    node = _parse("(a, b, c)")
    assert list(get_bindings(node)) == []


def test_tuple_bindings_unpack():
    node = _parse("(a, b, *rest)")
    assert list(get_bindings(node)) == []


def test_tuple_bindings_walrus():
    node = _parse("(a, (b := genb()), c)")
    assert list(get_bindings(node)) == ["b"]


def test_tuple_bindings_walrus_unpack():
    node = _parse("(a, b, *(rest := other))")
    assert list(get_bindings(node)) == ["rest"]


def test_formatted_value_bindings():
    """
    ..code:: python

        FormattedValue(expr value, int conversion, expr? format_spec)
    """
    node = _parse("f'{a} {b} {c}'")
    assert list(get_bindings(node)) == []


def test_formatted_value_bindings_walrus():
    node = _parse("f'{a} {1 + (b := 1)} {c}'")
    assert list(get_bindings(node)) == ["b"]


def test_formatted_value_bindings_format_spec_walrus():
    node = _parse("f'{a} {b:{0 + (c := 0.3)}} {d}'")
    assert list(get_bindings(node)) == ["c"]


@match_statement
def test_match_statement_bindings_literal():
    node = _parse(
        """
        match a:
            case True:
                pass
        """
    )
    assert list(get_bindings(node)) == []


@match_statement
def test_match_statement_bindings_capture():
    node = _parse(
        """
        match a:
            case b:
                pass
        """
    )
    assert list(get_bindings(node)) == ["b"]


@match_statement
def test_match_statement_bindings_wildcard():
    node = _parse(
        """
        match a:
            case _:
                pass
        """
    )
    assert list(get_bindings(node)) == []


@match_statement
def test_match_statement_bindings_constant():
    node = _parse(
        """
        match a:
            case 1:
                pass
        """
    )
    assert list(get_bindings(node)) == []


@match_statement
def test_match_statement_bindings_named_constant():
    node = _parse(
        """
        match a:
            case MyEnum.CONSTANT:
                pass
        """
    )
    assert list(get_bindings(node)) == []


@match_statement
def test_match_statement_bindings_sequence():
    node = _parse(
        """
        match a:
            case [b, *c, d, _]:
                pass
        """
    )
    assert list(get_bindings(node)) == ["b", "c", "d"]


@match_statement
def test_match_statement_bindings_sequence_wildcard():
    node = _parse(
        """
        match a:
            case [*_]:
                pass
        """
    )
    assert list(get_bindings(node)) == []


@match_statement
def test_match_statement_bindings_mapping():
    node = _parse(
        """
        match a:
            case {"k1": "v1", "k2": b, "k3": _, **c}:
                pass
        """
    )
    assert list(get_bindings(node)) == ["b", "c"]


@match_statement
def test_match_statement_bindings_class():
    node = _parse(
        """
        match a:
            case MyClass(0, b, x=_, y=c):
                pass
        """
    )
    assert list(get_bindings(node)) == ["b", "c"]


@match_statement
def test_match_statement_bindings_or():
    node = _parse(
        """
        match a:
            case b | c:
                pass
        """
    )
    assert list(get_bindings(node)) == ["b", "c"]


@match_statement
def test_match_statement_bindings_as():
    node = _parse(
        """
        match a:
            case b as c:
                pass
        """
    )
    assert list(get_bindings(node)) == ["b", "c"]
