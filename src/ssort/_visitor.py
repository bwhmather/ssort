from __future__ import annotations

import ast
import functools
import sys
import typing

T = typing.TypeVar("T")


def node_visitor(func: typing.Callable[[ast.AST], typing.Iterable[T]]):
    """Decorator for AST node visitor functions.

    Has much better performance than its equivalents in the `ast` module.
    """
    func = functools.singledispatch(func)

    @func.register(ast.Module)
    def visit_module(node: ast.Module) -> typing.Iterable[T]:
        for statement in node.body:
            yield from func(statement)
        for type_ignore in node.type_ignores:
            yield from func(type_ignore)

    @func.register(ast.Interactive)
    def visit_interactive(node: ast.Interactive) -> typing.Iterable[T]:
        for statement in node.body:
            yield from func(statement)

    @func.register(ast.Expression)
    def visit_expression(node: ast.Expression) -> typing.Iterable[T]:
        yield from func(node.body)

    @func.register(ast.FunctionType)
    def visit_function_type(node: ast.FunctionType) -> typing.Iterable[T]:
        for argtype in node.argtypes:
            yield from func(argtype)
        yield from func(node.returns)

    @func.register(ast.FunctionDef)
    @func.register(ast.AsyncFunctionDef)
    def visit_function_def(
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> typing.Iterable[T]:
        for decorator in node.decorator_list:
            yield from func(decorator)
        yield from func(node.args)
        if node.returns is not None:
            yield from func(node.returns)
        for statement in node.body:
            yield from func(statement)

    @func.register(ast.ClassDef)
    def visit_class_def(node: ast.ClassDef) -> typing.Iterable[T]:
        for decorator in node.decorator_list:
            yield from func(decorator)
        for base in node.bases:
            yield from func(base)
        for keyword in node.keywords:
            yield from func(keyword)
        for statement in node.body:
            yield from func(statement)

    @func.register(ast.Return)
    def visit_return(node: ast.Return) -> typing.Iterable[T]:
        if node.value is not None:
            yield from func(node.value)

    @func.register(ast.Delete)
    def visit_delete(node: ast.Delete) -> typing.Iterable[T]:
        for target in node.targets:
            yield from func(target)

    @func.register(ast.Assign)
    def visit_assign(node: ast.Assign) -> typing.Iterable[T]:
        for target in node.targets:
            yield from func(target)
        yield from func(node.value)

    @func.register(ast.AugAssign)
    def visit_aug_assign(node: ast.AugAssign) -> typing.Iterable[T]:
        yield from func(node.target)
        yield from func(node.value)

    @func.register(ast.AnnAssign)
    def visit_ann_assign(node: ast.AnnAssign) -> typing.Iterable[T]:
        yield from func(node.target)
        yield from func(node.annotation)
        if node.value is not None:
            yield from func(node.value)

    @func.register(ast.For)
    @func.register(ast.AsyncFor)
    def visit_for(node: ast.For | ast.AsyncFor) -> typing.Iterable[T]:
        yield from func(node.target)
        yield from func(node.iter)
        for statement in node.body:
            yield from func(statement)
        for statement in node.orelse:
            yield from func(statement)

    @func.register(ast.While)
    def visit_while(node: ast.While) -> typing.Iterable[T]:
        yield from func(node.test)
        for statement in node.body:
            yield from func(statement)
        for statement in node.orelse:
            yield from func(statement)

    @func.register(ast.If)
    def visit_if(node: ast.If) -> typing.Iterable[T]:
        yield from func(node.test)
        for statement in node.body:
            yield from func(statement)
        for statement in node.orelse:
            yield from func(statement)

    @func.register(ast.With)
    @func.register(ast.AsyncWith)
    def visit_with(node: ast.With | ast.AsyncWith) -> typing.Iterable[T]:
        for item in node.items:
            yield from func(item)
        for statement in node.body:
            yield from func(statement)

    if sys.version_info >= (3, 10):

        @func.register(ast.Match)
        def visit_match(node: ast.Match) -> typing.Iterable[T]:
            yield from func(node.subject)
            for case in node.cases:
                yield from func(case)

    @func.register(ast.Raise)
    def visit_raise(node: ast.Raise) -> typing.Iterable[T]:
        if node.exc is not None:
            yield from func(node.exc)
        if node.cause is not None:
            yield from func(node.cause)

    @func.register(ast.Try)
    def visit_try(node: ast.Try) -> typing.Iterable[T]:
        for statement in node.body:
            yield from func(statement)
        for handler in node.handlers:
            yield from func(handler)
        for statement in node.orelse:
            yield from func(statement)
        for statement in node.finalbody:
            yield from func(statement)

    @func.register(ast.Assert)
    def visit_assert(node: ast.Assert) -> typing.Iterable[T]:
        yield from func(node.test)
        if node.msg is not None:
            yield from func(node.msg)

    @func.register(ast.Import)
    def visit_import(node: ast.Import) -> typing.Iterable[T]:
        for name in node.names:
            yield from func(name)

    @func.register(ast.ImportFrom)
    def visit_import_from(node: ast.ImportFrom) -> typing.Iterable[T]:
        for name in node.names:
            yield from func(name)

    @func.register(ast.Global)
    def visit_global(_: ast.Global) -> typing.Iterable[T]:
        return ()

    @func.register(ast.Nonlocal)
    def visit_nonlocal(_: ast.Nonlocal) -> typing.Iterable[T]:
        return ()

    @func.register(ast.Expr)
    def visit_expr(node: ast.Expr) -> typing.Iterable[T]:
        yield from func(node.value)

    @func.register(ast.Pass)
    def visit_pass(_: ast.Pass) -> typing.Iterable[T]:
        return ()

    @func.register(ast.Break)
    def visit_break(_: ast.Break) -> typing.Iterable[T]:
        return ()

    @func.register(ast.Continue)
    def visit_continue(_: ast.Continue) -> typing.Iterable[T]:
        return ()

    @func.register(ast.BoolOp)
    def visit_bool_op(node: ast.BoolOp) -> typing.Iterable[T]:
        for value in node.values:
            yield from func(value)

    @func.register(ast.NamedExpr)
    def visit_named_expr(node: ast.NamedExpr) -> typing.Iterable[T]:
        yield from func(node.target)
        yield from func(node.value)

    @func.register(ast.BinOp)
    def visit_bin_op(node: ast.BinOp) -> typing.Iterable[T]:
        yield from func(node.left)
        yield from func(node.right)

    @func.register(ast.UnaryOp)
    def visit_unary_op(node: ast.UnaryOp) -> typing.Iterable[T]:
        yield from func(node.operand)

    @func.register(ast.Lambda)
    def visit_lambda(node: ast.Lambda) -> typing.Iterable[T]:
        yield from func(node.args)
        yield from func(node.body)

    @func.register(ast.IfExp)
    def visit_if_exp(node: ast.IfExp) -> typing.Iterable[T]:
        yield from func(node.test)
        yield from func(node.body)
        yield from func(node.orelse)

    @func.register(ast.Dict)
    def visit_dict(node: ast.Dict) -> typing.Iterable[T]:
        for key in node.keys:
            if key is not None:
                yield from func(key)
        for value in node.values:
            yield from func(value)

    @func.register(ast.Set)
    def visit_set(node: ast.Set) -> typing.Iterable[T]:
        for elt in node.elts:
            yield from func(elt)

    @func.register(ast.ListComp)
    def visit_list_comp(node: ast.ListComp) -> typing.Iterable[T]:
        yield from func(node.elt)
        for generator in node.generators:
            yield from func(generator)

    @func.register(ast.SetComp)
    def visit_set_comp(node: ast.SetComp) -> typing.Iterable[T]:
        yield from func(node.elt)
        for generator in node.generators:
            yield from func(generator)

    @func.register(ast.DictComp)
    def visit_dict_comp(node: ast.DictComp) -> typing.Iterable[T]:
        yield from func(node.key)
        yield from func(node.value)
        for generator in node.generators:
            yield from func(generator)

    @func.register(ast.GeneratorExp)
    def visit_generator_exp(node: ast.GeneratorExp) -> typing.Iterable[T]:
        yield from func(node.elt)
        for generator in node.generators:
            yield from func(generator)

    @func.register(ast.Await)
    def visit_await(node: ast.Await) -> typing.Iterable[T]:
        yield from func(node.value)

    @func.register(ast.Yield)
    def visit_yield(node: ast.Yield) -> typing.Iterable[T]:
        if node.value is not None:
            yield from func(node.value)

    @func.register(ast.YieldFrom)
    def visit_yield_from(node: ast.YieldFrom) -> typing.Iterable[T]:
        yield from func(node.value)

    @func.register(ast.Compare)
    def visit_compare(node: ast.Compare) -> typing.Iterable[T]:
        yield from func(node.left)
        for comparator in node.comparators:
            yield from func(comparator)

    @func.register(ast.Call)
    def visit_call(node: ast.Call) -> typing.Iterable[T]:
        yield from func(node.func)
        for arg in node.args:
            yield from func(arg)
        for keyword in node.keywords:
            yield from func(keyword)

    @func.register(ast.FormattedValue)
    def visit_formatted_value(node: ast.FormattedValue) -> typing.Iterable[T]:
        yield from func(node.value)
        if node.format_spec is not None:
            yield from func(node.format_spec)

    @func.register(ast.JoinedStr)
    def visit_joined_str(node: ast.JoinedStr) -> typing.Iterable[T]:
        for value in node.values:
            yield from func(value)

    @func.register(ast.Constant)
    def visit_constant(_: ast.Constant) -> typing.Iterable[T]:
        return ()

    @func.register(ast.Attribute)
    def visit_attribute(node: ast.Attribute) -> typing.Iterable[T]:
        yield from func(node.value)

    @func.register(ast.Subscript)
    def visit_subscript(node: ast.Subscript) -> typing.Iterable[T]:
        yield from func(node.value)
        yield from func(node.slice)

    @func.register(ast.Starred)
    def visit_starred(node: ast.Starred) -> typing.Iterable[T]:
        yield from func(node.value)

    @func.register(ast.Name)
    def visit_name(_: ast.Name) -> typing.Iterable[T]:
        return ()

    @func.register(ast.List)
    def visit_list(node: ast.List) -> typing.Iterable[T]:
        for elt in node.elts:
            yield from func(elt)

    @func.register(ast.Tuple)
    def visit_tuple(node: ast.Tuple) -> typing.Iterable[T]:
        for elt in node.elts:
            yield from func(elt)

    @func.register(ast.Slice)
    def visit_slice(node: ast.Slice) -> typing.Iterable[T]:
        if node.lower is not None:
            yield from func(node.lower)
        if node.upper is not None:
            yield from func(node.upper)
        if node.step is not None:
            yield from func(node.step)

    if sys.version_info < (3, 9):

        @func.register(ast.ExtSlice)
        def visit_ext_slice(node: ast.ExtSlice) -> typing.Iterable[T]:
            for dim in node.dims:
                yield from func(dim)

        @func.register(ast.Index)
        def visit_index(node: ast.Index) -> typing.Iterable[T]:
            yield from func(node.value)

    @func.register(ast.comprehension)
    def visit_comprehension(node: ast.comprehension) -> typing.Iterable[T]:
        yield from func(node.target)
        yield from func(node.iter)
        for ifs in node.ifs:
            yield from func(ifs)

    @func.register(ast.ExceptHandler)
    def visit_except_handler(node: ast.ExceptHandler) -> typing.Iterable[T]:
        if node.type is not None:
            yield from func(node.type)
        for statement in node.body:
            yield from func(statement)

    @func.register(ast.arguments)
    def visit_arguments(node: ast.arguments) -> typing.Iterable[T]:
        for arg in node.posonlyargs:
            yield from func(arg)
        for arg in node.args:
            yield from func(arg)
        if node.vararg is not None:
            yield from func(node.vararg)
        for arg in node.kwonlyargs:
            yield from func(arg)
        for default in node.kw_defaults:
            if default is not None:
                yield from func(default)
        if node.kwarg is not None:
            yield from func(node.kwarg)
        for default in node.defaults:
            yield from func(default)

    @func.register(ast.arg)
    def visit_arg(node: ast.arg) -> typing.Iterable[T]:
        if node.annotation is not None:
            yield from func(node.annotation)

    @func.register(ast.keyword)
    def visit_keyword(node: ast.keyword) -> typing.Iterable[T]:
        yield from func(node.value)

    @func.register(ast.alias)
    def visit_alias(_: ast.alias) -> typing.Iterable[T]:
        return ()

    @func.register(ast.withitem)
    def visit_withitem(node: ast.withitem) -> typing.Iterable[T]:
        yield from func(node.context_expr)
        if node.optional_vars is not None:
            yield from func(node.optional_vars)

    if sys.version_info >= (3, 10):

        @func.register(ast.match_case)
        def visit_match_case(node: ast.match_case) -> typing.Iterable[T]:
            yield from func(node.pattern)
            if node.guard is not None:
                yield from func(node.guard)
            for statement in node.body:
                yield from func(statement)

        @func.register(ast.MatchValue)
        def visit_match_value(node: ast.MatchValue) -> typing.Iterable[T]:
            yield from func(node.value)

        @func.register(ast.MatchSingleton)
        def visit_match_singleton(_: ast.MatchSingleton) -> typing.Iterable[T]:
            return ()

        @func.register(ast.MatchSequence)
        def visit_match_sequence(
            node: ast.MatchSequence,
        ) -> typing.Iterable[T]:
            for pattern in node.patterns:
                yield from func(pattern)

        @func.register(ast.MatchMapping)
        def visit_match_mapping(node: ast.MatchMapping) -> typing.Iterable[T]:
            for key in node.keys:
                yield from func(key)
            for pattern in node.patterns:
                yield from func(pattern)
            if node.rest is not None:
                yield from func(node.rest)

        @func.register(ast.MatchClass)
        def visit_match_class(node: ast.MatchClass) -> typing.Iterable[T]:
            yield from func(node.cls)
            for pattern in node.patterns:
                yield from func(pattern)
            for kwd_pattern in node.kwd_patterns:
                yield from func(kwd_pattern)

        @func.register(ast.MatchStar)
        def visit_match_star(_: ast.MatchStar) -> typing.Iterable[T]:
            return ()

        @func.register(ast.MatchAs)
        def visit_match_as(node: ast.MatchAs) -> typing.Iterable[T]:
            if node.pattern is not None:
                yield from func(node.pattern)

        @func.register(ast.MatchOr)
        def visit_match_or(node: ast.MatchOr) -> typing.Iterable[T]:
            for pattern in node.patterns:
                yield from func(pattern)

    @func.register(ast.type_ignore)
    def visit_type_ignore(_: ast.type_ignore) -> typing.Iterable[T]:
        return ()

    return func
