from __future__ import annotations

import ast
import sys
from typing import Callable, Generic, Iterable, Type, TypeVar

_T = TypeVar("_T")
_Visitor = Callable[[ast.AST], Iterable[_T]]


class NodeVisitor(Generic[_T]):
    def __init__(self) -> None:
        self._visitors = {}

    def register(
        self, *node_types: Type[ast.AST]
    ) -> Callable[[_Visitor], _Visitor]:
        def delegate(visitor: _Visitor) -> _Visitor:
            for node_type in node_types:
                self._visitors[node_type] = visitor
            return visitor

        return delegate

    def visit(self, node: ast.AST) -> Iterable[_T]:
        visitor = self._visitors.get(type(node))
        if visitor is not None:
            return visitor(node)
        return self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> Iterable[_T]:
        try:
            visitor = _generic_visitors[type(node)]
        except KeyError:
            raise NotImplementedError(
                f"No visitor for type {type(node).__name__}"
            )
        return visitor(self, node)


_GenericVisitor = Callable[[NodeVisitor, ast.AST], Iterable]
_generic_visitors: dict[Type[ast.AST], _GenericVisitor] = {}


def _register_generic_visitor(
    *node_types: Type[ast.AST],
) -> Callable[[_GenericVisitor], _GenericVisitor]:
    def decorator(func: _GenericVisitor) -> _GenericVisitor:
        for node_type in node_types:
            _generic_visitors[node_type] = func
        return func

    return decorator


@_register_generic_visitor(ast.Module)
def _visit_module(visitor: NodeVisitor, node: ast.Module) -> Iterable:
    for statement in node.body:
        yield from visitor.visit(statement)
    for type_ignore in node.type_ignores:
        yield from visitor.visit(type_ignore)


@_register_generic_visitor(ast.Interactive)
def _visit_interactive(
    visitor: NodeVisitor, node: ast.Interactive
) -> Iterable:
    for statement in node.body:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.Expression)
def _visit_expression(visitor: NodeVisitor, node: ast.Expression) -> Iterable:
    yield from visitor.visit(node.body)


@_register_generic_visitor(ast.FunctionType)
def _visit_function_type(
    visitor: NodeVisitor, node: ast.FunctionType
) -> Iterable:
    for argtype in node.argtypes:
        yield from visitor.visit(argtype)
    yield from visitor.visit(node.returns)


@_register_generic_visitor(ast.FunctionDef)
def _visit_function_def(
    visitor: NodeVisitor, node: ast.FunctionDef
) -> Iterable:
    for decorator in node.decorator_list:
        yield from visitor.visit(decorator)
    yield from visitor.visit(node.args)
    if node.returns is not None:
        yield from visitor.visit(node.returns)
    for statement in node.body:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.AsyncFunctionDef)
def _visit_async_function_def(
    visitor: NodeVisitor, node: ast.AsyncFunctionDef
) -> Iterable:
    for decorator in node.decorator_list:
        yield from visitor.visit(decorator)
    yield from visitor.visit(node.args)
    if node.returns is not None:
        yield from visitor.visit(node.returns)
    for statement in node.body:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.ClassDef)
def _visit_class_def(visitor: NodeVisitor, node: ast.ClassDef) -> Iterable:
    for decorator in node.decorator_list:
        yield from visitor.visit(decorator)
    for base in node.bases:
        yield from visitor.visit(base)
    for keyword in node.keywords:
        yield from visitor.visit(keyword)
    for statement in node.body:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.Return)
def _visit_return(visitor: NodeVisitor, node: ast.Return) -> Iterable:
    if node.value is not None:
        yield from visitor.visit(node.value)


@_register_generic_visitor(ast.Delete)
def _visit_delete(visitor: NodeVisitor, node: ast.Delete) -> Iterable:
    for target in node.targets:
        yield from visitor.visit(target)


@_register_generic_visitor(ast.Assign)
def _visit_assign(visitor: NodeVisitor, node: ast.Assign) -> Iterable:
    for target in node.targets:
        yield from visitor.visit(target)
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.AugAssign)
def _visit_aug_assign(visitor: NodeVisitor, node: ast.AugAssign) -> Iterable:
    yield from visitor.visit(node.target)
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.AnnAssign)
def _visit_ann_assign(visitor: NodeVisitor, node: ast.AnnAssign) -> Iterable:
    yield from visitor.visit(node.target)
    yield from visitor.visit(node.annotation)
    if node.value is not None:
        yield from visitor.visit(node.value)


@_register_generic_visitor(ast.For)
def _visit_for(visitor: NodeVisitor, node: ast.For) -> Iterable:
    yield from visitor.visit(node.target)
    yield from visitor.visit(node.iter)
    for statement in node.body:
        yield from visitor.visit(statement)
    for statement in node.orelse:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.AsyncFor)
def _visit_async_for(visitor: NodeVisitor, node: ast.AsyncFor) -> Iterable:
    yield from visitor.visit(node.target)
    yield from visitor.visit(node.iter)
    for statement in node.body:
        yield from visitor.visit(statement)
    for statement in node.orelse:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.While)
def _visit_while(visitor: NodeVisitor, node: ast.While) -> Iterable:
    yield from visitor.visit(node.test)
    for statement in node.body:
        yield from visitor.visit(statement)
    for statement in node.orelse:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.If)
def _visit_if(visitor: NodeVisitor, node: ast.If) -> Iterable:
    yield from visitor.visit(node.test)
    for statement in node.body:
        yield from visitor.visit(statement)
    for statement in node.orelse:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.With)
def _visit_with(visitor: NodeVisitor, node: ast.With) -> Iterable:
    for item in node.items:
        yield from visitor.visit(item)
    for statement in node.body:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.AsyncWith)
def _visit_async_with(visitor: NodeVisitor, node: ast.AsyncWith) -> Iterable:
    for item in node.items:
        yield from visitor.visit(item)
    for statement in node.body:
        yield from visitor.visit(statement)


if sys.version_info >= (3, 10):

    @_register_generic_visitor(ast.Match)
    def _visit_match(visitor: NodeVisitor, node: ast.Match) -> Iterable:
        yield from visitor.visit(node.subject)
        for case in node.cases:
            yield from visitor.visit(case)


@_register_generic_visitor(ast.Raise)
def _visit_raise(visitor: NodeVisitor, node: ast.Raise) -> Iterable:
    if node.exc is not None:
        yield from visitor.visit(node.exc)
    if node.cause is not None:
        yield from visitor.visit(node.cause)


@_register_generic_visitor(ast.Try)
def _visit_try(visitor: NodeVisitor, node: ast.Try) -> Iterable:
    for statement in node.body:
        yield from visitor.visit(statement)
    for handler in node.handlers:
        yield from visitor.visit(handler)
    for statement in node.orelse:
        yield from visitor.visit(statement)
    for statement in node.finalbody:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.Assert)
def _visit_assert(visitor: NodeVisitor, node: ast.Assert) -> Iterable:
    yield from visitor.visit(node.test)
    if node.msg is not None:
        yield from visitor.visit(node.msg)


@_register_generic_visitor(ast.Import)
def _visit_import(visitor: NodeVisitor, node: ast.Import) -> Iterable:
    for name in node.names:
        yield from visitor.visit(name)


@_register_generic_visitor(ast.ImportFrom)
def _visit_import_from(visitor: NodeVisitor, node: ast.ImportFrom) -> Iterable:
    for name in node.names:
        yield from visitor.visit(name)


@_register_generic_visitor(ast.Global)
def _visit_global(visitor: NodeVisitor, node: ast.Global) -> Iterable:
    return ()


@_register_generic_visitor(ast.Nonlocal)
def _visit_nonlocal(visitor: NodeVisitor, node: ast.Nonlocal) -> Iterable:
    return ()


@_register_generic_visitor(ast.Expr)
def _visit_expr(visitor: NodeVisitor, node: ast.Expr) -> Iterable:
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.Pass)
def _visit_pass(visitor: NodeVisitor, node: ast.Pass) -> Iterable:
    return ()


@_register_generic_visitor(ast.Break)
def _visit_break(visitor: NodeVisitor, node: ast.Break) -> Iterable:
    return ()


@_register_generic_visitor(ast.Continue)
def _visit_continue(visitor: NodeVisitor, node: ast.Continue) -> Iterable:
    return ()


@_register_generic_visitor(ast.BoolOp)
def _visit_bool_op(visitor: NodeVisitor, node: ast.BoolOp) -> Iterable:
    for value in node.values:
        yield from visitor.visit(value)


@_register_generic_visitor(ast.NamedExpr)
def _visit_named_expr(visitor: NodeVisitor, node: ast.NamedExpr) -> Iterable:
    yield from visitor.visit(node.target)
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.BinOp)
def _visit_bin_op(visitor: NodeVisitor, node: ast.BinOp) -> Iterable:
    yield from visitor.visit(node.left)
    yield from visitor.visit(node.right)


@_register_generic_visitor(ast.UnaryOp)
def _visit_unary_op(visitor: NodeVisitor, node: ast.UnaryOp) -> Iterable:
    yield from visitor.visit(node.operand)


@_register_generic_visitor(ast.Lambda)
def _visit_lambda(visitor: NodeVisitor, node: ast.Lambda) -> Iterable:
    yield from visitor.visit(node.args)
    yield from visitor.visit(node.body)


@_register_generic_visitor(ast.IfExp)
def _visit_if_exp(visitor: NodeVisitor, node: ast.IfExp) -> Iterable:
    yield from visitor.visit(node.test)
    yield from visitor.visit(node.body)
    yield from visitor.visit(node.orelse)


@_register_generic_visitor(ast.Dict)
def _visit_dict(visitor: NodeVisitor, node: ast.Dict) -> Iterable:
    for key in node.keys:
        if key is not None:
            yield from visitor.visit(key)
    for value in node.values:
        yield from visitor.visit(value)


@_register_generic_visitor(ast.Set)
def _visit_set(visitor: NodeVisitor, node: ast.Set) -> Iterable:
    for elt in node.elts:
        yield from visitor.visit(elt)


@_register_generic_visitor(ast.ListComp)
def _visit_list_comp(visitor: NodeVisitor, node: ast.ListComp) -> Iterable:
    yield from visitor.visit(node.elt)
    for generator in node.generators:
        yield from visitor.visit(generator)


@_register_generic_visitor(ast.SetComp)
def _visit_set_comp(visitor: NodeVisitor, node: ast.SetComp) -> Iterable:
    yield from visitor.visit(node.elt)
    for generator in node.generators:
        yield from visitor.visit(generator)


@_register_generic_visitor(ast.DictComp)
def _visit_dict_comp(visitor: NodeVisitor, node: ast.DictComp) -> Iterable:
    yield from visitor.visit(node.key)
    yield from visitor.visit(node.value)
    for generator in node.generators:
        yield from visitor.visit(generator)


@_register_generic_visitor(ast.GeneratorExp)
def _visit_generator_exp(
    visitor: NodeVisitor, node: ast.GeneratorExp
) -> Iterable:
    yield from visitor.visit(node.elt)
    for generator in node.generators:
        yield from visitor.visit(generator)


@_register_generic_visitor(ast.Await)
def _visit_await(visitor: NodeVisitor, node: ast.Await) -> Iterable:
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.Yield)
def _visit_yield(visitor: NodeVisitor, node: ast.Yield) -> Iterable:
    if node.value is not None:
        yield from visitor.visit(node.value)


@_register_generic_visitor(ast.YieldFrom)
def _visit_yield_from(visitor: NodeVisitor, node: ast.YieldFrom) -> Iterable:
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.Compare)
def _visit_compare(visitor: NodeVisitor, node: ast.Compare) -> Iterable:
    yield from visitor.visit(node.left)
    for comparator in node.comparators:
        yield from visitor.visit(comparator)


@_register_generic_visitor(ast.Call)
def _visit_call(visitor: NodeVisitor, node: ast.Call) -> Iterable:
    yield from visitor.visit(node.func)
    for arg in node.args:
        yield from visitor.visit(arg)
    for keyword in node.keywords:
        yield from visitor.visit(keyword)


@_register_generic_visitor(ast.FormattedValue)
def _visit_formatted_value(
    visitor: NodeVisitor, node: ast.FormattedValue
) -> Iterable:
    yield from visitor.visit(node.value)
    if node.format_spec is not None:
        yield from visitor.visit(node.format_spec)


@_register_generic_visitor(ast.JoinedStr)
def _visit_joined_str(visitor: NodeVisitor, node: ast.JoinedStr) -> Iterable:
    for value in node.values:
        yield from visitor.visit(value)


@_register_generic_visitor(ast.Constant)
def _visit_constant(visitor: NodeVisitor, node: ast.Constant) -> Iterable:
    return ()


@_register_generic_visitor(ast.Attribute)
def _visit_attribute(visitor: NodeVisitor, node: ast.Attribute) -> Iterable:
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.Subscript)
def _visit_subscript(visitor: NodeVisitor, node: ast.Subscript) -> Iterable:
    yield from visitor.visit(node.value)
    yield from visitor.visit(node.slice)


@_register_generic_visitor(ast.Starred)
def _visit_starred(visitor: NodeVisitor, node: ast.Starred) -> Iterable:
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.Name)
def _visit_name(visitor: NodeVisitor, node: ast.Name) -> Iterable:
    return ()


@_register_generic_visitor(ast.List)
def _visit_list(visitor: NodeVisitor, node: ast.List) -> Iterable:
    for elt in node.elts:
        yield from visitor.visit(elt)


@_register_generic_visitor(ast.Tuple)
def _visit_tuple(visitor: NodeVisitor, node: ast.Tuple) -> Iterable:
    for elt in node.elts:
        yield from visitor.visit(elt)


@_register_generic_visitor(ast.Slice)
def _visit_slice(visitor: NodeVisitor, node: ast.Slice) -> Iterable:
    if node.lower is not None:
        yield from visitor.visit(node.lower)
    if node.upper is not None:
        yield from visitor.visit(node.upper)
    if node.step is not None:
        yield from visitor.visit(node.step)


if sys.version_info < (3, 9):

    @_register_generic_visitor(ast.ExtSlice)
    def _visit_ext_slice(visitor: NodeVisitor, node: ast.ExtSlice) -> Iterable:
        for dim in node.dims:
            yield from visitor.visit(dim)

    @_register_generic_visitor(ast.Index)
    def _visit_index(visitor: NodeVisitor, node: ast.Index) -> Iterable:
        yield from visitor.visit(node.value)


@_register_generic_visitor(ast.comprehension)
def _visit_comprehension(
    visitor: NodeVisitor, node: ast.comprehension
) -> Iterable:
    yield from visitor.visit(node.target)
    yield from visitor.visit(node.iter)
    for ifs in node.ifs:
        yield from visitor.visit(ifs)


@_register_generic_visitor(ast.ExceptHandler)
def _visit_except_handler(
    visitor: NodeVisitor, node: ast.ExceptHandler
) -> Iterable:
    if node.type is not None:
        yield from visitor.visit(node.type)
    for statement in node.body:
        yield from visitor.visit(statement)


@_register_generic_visitor(ast.arguments)
def _visit_arguments(visitor: NodeVisitor, node: ast.arguments) -> Iterable:
    for arg in node.posonlyargs:
        yield from visitor.visit(arg)
    for arg in node.args:
        yield from visitor.visit(arg)
    if node.vararg is not None:
        yield from visitor.visit(node.vararg)
    for arg in node.kwonlyargs:
        yield from visitor.visit(arg)
    for default in node.kw_defaults:
        if default is not None:
            yield from visitor.visit(default)
    if node.kwarg is not None:
        yield from visitor.visit(node.kwarg)
    for default in node.defaults:
        yield from visitor.visit(default)


@_register_generic_visitor(ast.arg)
def _visit_arg(visitor: NodeVisitor, node: ast.arg) -> Iterable:
    if node.annotation is not None:
        yield from visitor.visit(node.annotation)


@_register_generic_visitor(ast.keyword)
def _visit_keyword(visitor: NodeVisitor, node: ast.keyword) -> Iterable:
    yield from visitor.visit(node.value)


@_register_generic_visitor(ast.alias)
def _visit_alias(visitor: NodeVisitor, node: ast.alias) -> Iterable:
    return ()


@_register_generic_visitor(ast.withitem)
def _visit_withitem(visitor: NodeVisitor, node: ast.withitem) -> Iterable:
    yield from visitor.visit(node.context_expr)
    if node.optional_vars is not None:
        yield from visitor.visit(node.optional_vars)


if sys.version_info >= (3, 10):

    @_register_generic_visitor(ast.match_case)
    def _visit_match_case(
        visitor: NodeVisitor, node: ast.match_case
    ) -> Iterable:
        yield from visitor.visit(node.pattern)
        if node.guard is not None:
            yield from visitor.visit(node.guard)
        for statement in node.body:
            yield from visitor.visit(statement)

    @_register_generic_visitor(ast.MatchValue)
    def _visit_match_value(
        visitor: NodeVisitor, node: ast.MatchValue
    ) -> Iterable:
        yield from visitor.visit(node.value)

    @_register_generic_visitor(ast.MatchSingleton)
    def _visit_match_singleton(
        visitor: NodeVisitor, node: ast.MatchSingleton
    ) -> Iterable:
        return ()

    @_register_generic_visitor(ast.MatchSequence)
    def _visit_match_sequence(
        visitor: NodeVisitor, node: ast.MatchSequence
    ) -> Iterable:
        for pattern in node.patterns:
            yield from visitor.visit(pattern)

    @_register_generic_visitor(ast.MatchMapping)
    def _visit_match_mapping(
        visitor: NodeVisitor, node: ast.MatchMapping
    ) -> Iterable:
        for key in node.keys:
            yield from visitor.visit(key)
        for pattern in node.patterns:
            yield from visitor.visit(pattern)

    @_register_generic_visitor(ast.MatchClass)
    def _visit_match_class(
        visitor: NodeVisitor, node: ast.MatchClass
    ) -> Iterable:
        yield from visitor.visit(node.cls)
        for pattern in node.patterns:
            yield from visitor.visit(pattern)
        for kwd_pattern in node.kwd_patterns:
            yield from visitor.visit(kwd_pattern)

    @_register_generic_visitor(ast.MatchStar)
    def _visit_match_star(
        visitor: NodeVisitor, node: ast.MatchStar
    ) -> Iterable:
        return ()

    @_register_generic_visitor(ast.MatchAs)
    def _visit_match_as(visitor: NodeVisitor, node: ast.MatchAs) -> Iterable:
        if node.pattern is not None:
            yield from visitor.visit(node.pattern)

    @_register_generic_visitor(ast.MatchOr)
    def _visit_match_or(visitor: NodeVisitor, node: ast.MatchOr) -> Iterable:
        for pattern in node.patterns:
            yield from visitor.visit(pattern)


@_register_generic_visitor(ast.type_ignore)
def _visit_type_ignore(
    visitor: NodeVisitor, node: ast.type_ignore
) -> Iterable:
    return ()
