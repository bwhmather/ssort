from __future__ import annotations

import ast
import sys
from typing import Iterable

from ssort._utils import single_dispatch


@single_dispatch
def iter_child_nodes(node: ast.AST) -> Iterable[ast.AST]:
    raise NotImplementedError(
        f"AST traversal for {type(node).__name__!r} is not implemented"
    )


@iter_child_nodes.register(ast.Module)
def _iter_child_nodes_of_module(node: ast.Module) -> Iterable[ast.AST]:
    yield from node.body
    yield from node.type_ignores


@iter_child_nodes.register(ast.Interactive)
def _iter_child_nodes_of_interactive(
    node: ast.Interactive,
) -> Iterable[ast.AST]:
    yield from node.body


@iter_child_nodes.register(ast.Expression)
def _iter_child_nodes_of_expression(node: ast.Expression) -> Iterable[ast.AST]:
    yield node.body


@iter_child_nodes.register(ast.FunctionType)
def _iter_child_nodes_of_function_type(
    node: ast.FunctionType,
) -> Iterable[ast.AST]:
    yield from node.argtypes
    yield node.returns


@iter_child_nodes.register(ast.FunctionDef)
@iter_child_nodes.register(ast.AsyncFunctionDef)
def _iter_child_nodes_of_function_def(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Iterable[ast.AST]:
    yield from node.decorator_list
    yield node.args
    if node.returns is not None:
        yield node.returns
    yield from node.body


@iter_child_nodes.register(ast.ClassDef)
def _iter_child_nodes_of_class_def(node: ast.ClassDef) -> Iterable[ast.AST]:
    yield from node.decorator_list
    yield from node.bases
    yield from node.keywords
    yield from node.body


@iter_child_nodes.register(ast.Return)
def _iter_child_nodes_of_return(node: ast.Return) -> Iterable[ast.AST]:
    if node.value is not None:
        yield node.value


@iter_child_nodes.register(ast.Delete)
def _iter_child_nodes_of_delete(node: ast.Delete) -> Iterable[ast.AST]:
    yield from node.targets


@iter_child_nodes.register(ast.Assign)
def _iter_child_nodes_of_assign(node: ast.Assign) -> Iterable[ast.AST]:
    yield from node.targets
    yield node.value


@iter_child_nodes.register(ast.AugAssign)
def _iter_child_nodes_of_aug_assign(node: ast.AugAssign) -> Iterable[ast.AST]:
    yield node.target
    yield node.value


@iter_child_nodes.register(ast.AnnAssign)
def _iter_child_nodes_of_ann_assign(node: ast.AnnAssign) -> Iterable[ast.AST]:
    yield node.target
    yield node.annotation
    if node.value is not None:
        yield node.value


@iter_child_nodes.register(ast.For)
@iter_child_nodes.register(ast.AsyncFor)
def _iter_child_nodes_of_for(
    node: ast.For | ast.AsyncFor,
) -> Iterable[ast.AST]:
    yield node.target
    yield node.iter
    yield from node.body
    yield from node.orelse


@iter_child_nodes.register(ast.While)
def _iter_child_nodes_of_while(node: ast.While) -> Iterable[ast.AST]:
    yield node.test
    yield from node.body
    yield from node.orelse


@iter_child_nodes.register(ast.If)
def _iter_child_nodes_of_if(node: ast.If) -> Iterable[ast.AST]:
    yield node.test
    yield from node.body
    yield from node.orelse


@iter_child_nodes.register(ast.With)
@iter_child_nodes.register(ast.AsyncWith)
def _iter_child_nodes_of_with(
    node: ast.With | ast.AsyncWith,
) -> Iterable[ast.AST]:
    yield from node.items
    yield from node.body


if sys.version_info >= (3, 10):

    @iter_child_nodes.register(ast.Match)
    def _iter_child_nodes_of_match(node: ast.Match) -> Iterable[ast.AST]:
        yield node.subject
        yield from node.cases


@iter_child_nodes.register(ast.Raise)
def _iter_child_nodes_of_raise(node: ast.Raise) -> Iterable[ast.AST]:
    if node.exc is not None:
        yield node.exc
    if node.cause is not None:
        yield node.cause


@iter_child_nodes.register(ast.Try)
def _iter_child_nodes_of_try(node: ast.Try) -> Iterable[ast.AST]:
    yield from node.body
    yield from node.handlers
    yield from node.orelse
    yield from node.finalbody


@iter_child_nodes.register(ast.Assert)
def _iter_child_nodes_of_assert(node: ast.Assert) -> Iterable[ast.AST]:
    yield node.test
    if node.msg is not None:
        yield node.msg


@iter_child_nodes.register(ast.Import)
def _iter_child_nodes_of_import(node: ast.Import) -> Iterable[ast.AST]:
    yield from node.names


@iter_child_nodes.register(ast.ImportFrom)
def _iter_child_nodes_of_import_from(
    node: ast.ImportFrom,
) -> Iterable[ast.AST]:
    yield from node.names


@iter_child_nodes.register(ast.Global)
@iter_child_nodes.register(ast.Nonlocal)
def _iter_child_nodes_of_scope(
    node: ast.Global | ast.Nonlocal,
) -> Iterable[ast.AST]:
    return ()


@iter_child_nodes.register(ast.Expr)
def _iter_child_nodes_of_expr(node: ast.Expr) -> Iterable[ast.AST]:
    yield node.value


@iter_child_nodes.register(ast.Pass)
@iter_child_nodes.register(ast.Break)
@iter_child_nodes.register(ast.Continue)
def _iter_child_nodes_of_control_flow(
    node: ast.Pass | ast.Break | ast.Continue,
) -> Iterable[ast.AST]:
    return ()


@iter_child_nodes.register(ast.BoolOp)
def _iter_child_nodes_of_bool_op(node: ast.BoolOp) -> Iterable[ast.AST]:
    yield from node.values


@iter_child_nodes.register(ast.NamedExpr)
def _iter_child_nodes_of_named_expr(node: ast.NamedExpr) -> Iterable[ast.AST]:
    yield node.target
    yield node.value


@iter_child_nodes.register(ast.BinOp)
def _iter_child_nodes_of_bin_op(node: ast.BinOp) -> Iterable[ast.AST]:
    yield node.left
    yield node.right


@iter_child_nodes.register(ast.UnaryOp)
def _iter_child_nodes_of_unary_op(node: ast.UnaryOp) -> Iterable[ast.AST]:
    yield node.operand


@iter_child_nodes.register(ast.Lambda)
def _iter_child_nodes_of_lambda(node: ast.Lambda) -> Iterable[ast.AST]:
    yield node.args
    yield node.body


@iter_child_nodes.register(ast.IfExp)
def _iter_child_nodes_of_if_exp(node: ast.IfExp) -> Iterable[ast.AST]:
    yield node.test
    yield node.body
    yield node.orelse


@iter_child_nodes.register(ast.Dict)
def _iter_child_nodes_of_dict(node: ast.Dict) -> Iterable[ast.AST]:
    for key in node.keys:
        if key is not None:
            yield key
    yield from node.values


@iter_child_nodes.register(ast.Set)
def _iter_child_nodes_of_set(node: ast.Set) -> Iterable[ast.AST]:
    yield from node.elts


@iter_child_nodes.register(ast.ListComp)
def _iter_child_nodes_of_list_comp(node: ast.ListComp) -> Iterable[ast.AST]:
    yield node.elt
    yield from node.generators


@iter_child_nodes.register(ast.SetComp)
def _iter_child_nodes_of_set_comp(node: ast.SetComp) -> Iterable[ast.AST]:
    yield node.elt
    yield from node.generators


@iter_child_nodes.register(ast.DictComp)
def _iter_child_nodes_of_dict_comp(node: ast.DictComp) -> Iterable[ast.AST]:
    yield node.key
    yield node.value
    yield from node.generators


@iter_child_nodes.register(ast.GeneratorExp)
def _iter_child_nodes_of_generator_exp(
    node: ast.GeneratorExp,
) -> Iterable[ast.AST]:
    yield node.elt
    yield from node.generators


@iter_child_nodes.register(ast.Await)
def _iter_child_nodes_of_await(node: ast.Await) -> Iterable[ast.AST]:
    yield node.value


@iter_child_nodes.register(ast.Yield)
def _iter_child_nodes_of_yield(node: ast.Yield) -> Iterable[ast.AST]:
    if node.value is not None:
        yield node.value


@iter_child_nodes.register(ast.YieldFrom)
def _iter_child_nodes_of_yield_from(node: ast.YieldFrom) -> Iterable[ast.AST]:
    yield node.value


@iter_child_nodes.register(ast.Compare)
def _iter_child_nodes_of_compare(node: ast.Compare) -> Iterable[ast.AST]:
    yield node.left
    yield from node.comparators


@iter_child_nodes.register(ast.Call)
def _iter_child_nodes_of_call(node: ast.Call) -> Iterable[ast.AST]:
    yield node.func
    yield from node.args
    yield from node.keywords


@iter_child_nodes.register(ast.FormattedValue)
def _iter_child_nodes_of_formatted_value(
    node: ast.FormattedValue,
) -> Iterable[ast.AST]:
    yield node.value
    if node.format_spec is not None:
        yield node.format_spec


@iter_child_nodes.register(ast.JoinedStr)
def _iter_child_nodes_of_joined_str(node: ast.JoinedStr) -> Iterable[ast.AST]:
    yield from node.values


@iter_child_nodes.register(ast.Constant)
def _iter_child_nodes_of_constant(node: ast.Constant) -> Iterable[ast.AST]:
    return ()


@iter_child_nodes.register(ast.Attribute)
def _iter_child_nodes_of_attribute(node: ast.Attribute) -> Iterable[ast.AST]:
    yield node.value


@iter_child_nodes.register(ast.Subscript)
def _iter_child_nodes_of_subscript(node: ast.Subscript) -> Iterable[ast.AST]:
    yield node.value
    yield node.slice


@iter_child_nodes.register(ast.Starred)
def _iter_child_nodes_of_starred(node: ast.Starred) -> Iterable[ast.AST]:
    yield node.value


@iter_child_nodes.register(ast.Name)
def _iter_child_nodes_of_name(node: ast.Name) -> Iterable[ast.AST]:
    return ()


@iter_child_nodes.register(ast.List)
@iter_child_nodes.register(ast.Tuple)
def _iter_child_nodes_of_sequence(
    node: ast.List | ast.Tuple,
) -> Iterable[ast.AST]:
    yield from node.elts


@iter_child_nodes.register(ast.Slice)
def _iter_child_nodes_of_slice(node: ast.Slice) -> Iterable[ast.AST]:
    if node.lower is not None:
        yield node.lower
    if node.upper is not None:
        yield node.upper
    if node.step is not None:
        yield node.step


if sys.version_info < (3, 9):

    @iter_child_nodes.register(ast.ExtSlice)
    def _iter_child_nodes_of_ext_slice(
        node: ast.ExtSlice,
    ) -> Iterable[ast.AST]:
        yield from node.dims

    @iter_child_nodes.register(ast.Index)
    def _iter_child_nodes_of_index(node: ast.Index) -> Iterable[ast.AST]:
        yield node.value


@iter_child_nodes.register(ast.comprehension)
def _iter_child_nodes_of_comprehension(
    node: ast.comprehension,
) -> Iterable[ast.AST]:
    yield node.target
    yield node.iter
    yield from node.ifs


@iter_child_nodes.register(ast.ExceptHandler)
def _iter_child_nodes_of_except_handler(
    node: ast.ExceptHandler,
) -> Iterable[ast.AST]:
    if node.type is not None:
        yield node.type
    yield from node.body


@iter_child_nodes.register(ast.arguments)
def _iter_child_nodes_of_arguments(node: ast.arguments) -> Iterable[ast.AST]:
    yield from node.posonlyargs
    yield from node.args
    if node.vararg is not None:
        yield node.vararg
    yield from node.kwonlyargs
    for default in node.kw_defaults:
        if default is not None:
            yield default
    if node.kwarg is not None:
        yield node.kwarg
    yield from node.defaults


@iter_child_nodes.register(ast.arg)
def _iter_child_nodes_of_arg(node: ast.arg) -> Iterable[ast.AST]:
    if node.annotation is not None:
        yield node.annotation


@iter_child_nodes.register(ast.keyword)
def _iter_child_nodes_of_keyword(node: ast.keyword) -> Iterable[ast.AST]:
    yield node.value


@iter_child_nodes.register(ast.alias)
def _iter_child_nodes_of_alias(node: ast.alias) -> Iterable[ast.AST]:
    return ()


@iter_child_nodes.register(ast.withitem)
def _iter_child_nodes_of_withitem(node: ast.withitem) -> Iterable[ast.AST]:
    yield node.context_expr
    if node.optional_vars is not None:
        yield node.optional_vars


if sys.version_info >= (3, 10):

    @iter_child_nodes.register(ast.match_case)
    def _iter_child_nodes_of_match_case(
        node: ast.match_case,
    ) -> Iterable[ast.AST]:
        yield node.pattern
        if node.guard is not None:
            yield node.guard
        yield from node.body

    @iter_child_nodes.register(ast.MatchValue)
    def _iter_child_nodes_of_match_value(
        node: ast.MatchValue,
    ) -> Iterable[ast.AST]:
        yield node.value

    @iter_child_nodes.register(ast.MatchSingleton)
    def _iter_child_nodes_of_match_singleton(
        node: ast.MatchSingleton,
    ) -> Iterable[ast.AST]:
        return ()

    @iter_child_nodes.register(ast.MatchSequence)
    def _iter_child_nodes_of_match_sequence(
        node: ast.MatchSequence,
    ) -> Iterable[ast.AST]:
        yield from node.patterns

    @iter_child_nodes.register(ast.MatchMapping)
    def _iter_child_nodes_of_match_mapping(
        node: ast.MatchMapping,
    ) -> Iterable[ast.AST]:
        yield from node.keys
        yield from node.patterns

    @iter_child_nodes.register(ast.MatchClass)
    def _iter_child_nodes_of_match_class(
        node: ast.MatchClass,
    ) -> Iterable[ast.AST]:
        yield node.cls
        yield from node.patterns
        yield from node.kwd_patterns

    @iter_child_nodes.register(ast.MatchStar)
    def _iter_child_nodes_of_match_star(
        node: ast.MatchStar,
    ) -> Iterable[ast.AST]:
        return ()

    @iter_child_nodes.register(ast.MatchAs)
    def _iter_child_nodes_of_match_as(node: ast.MatchAs) -> Iterable[ast.AST]:
        if node.pattern is not None:
            yield node.pattern

    @iter_child_nodes.register(ast.MatchOr)
    def _iter_child_nodes_of_match_or(node: ast.MatchOr) -> Iterable[ast.AST]:
        yield from node.patterns


@iter_child_nodes.register(ast.type_ignore)
def _iter_child_nodes_of_type_ignore(
    node: ast.type_ignore,
) -> Iterable[ast.AST]:
    return ()
