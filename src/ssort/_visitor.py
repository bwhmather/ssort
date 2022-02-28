from __future__ import annotations

import ast
import inspect
import sys
from typing import Callable, Generic, Iterable, Type, TypeVar

T = TypeVar("T")


def register_visitor(*node_types: Type[ast.AST]):
    def decorator(func):
        func._node_types = node_types
        return func

    return decorator


class NodeVisitor(Generic[T]):
    """A high performance AST node visitor.

    Provides an interface similar to `ast.NodeVisitor` but is much more
    performant.
    """

    _visitors: dict[type, Callable[[NodeVisitor, ast.AST], Iterable[T]]] = {}

    @classmethod
    def _find_visitor_methods(cls):
        cls._visitors = {}
        for name, member in inspect.getmembers(cls):
            node_types = getattr(member, "_node_types", None)
            if node_types is None:
                continue
            for node_type in node_types:
                cls._visitors[node_type] = member

    def __init_subclass__(cls, **kwargs):
        cls._find_visitor_methods()

    def visit(self, node: ast.AST) -> Iterable[T]:
        try:
            visitor = self._visitors[type(node)]
        except KeyError:
            raise NotImplementedError(
                f"Visitor for {type(node).__name__} has not been implemented"
            )
        return visitor(self, node)

    def generic_visit(self, node: ast.AST) -> Iterable[T]:
        try:
            visitor = NodeVisitor._visitors[type(node)]
        except KeyError:
            raise NotImplementedError(
                f"Visitor for {type(node).__name__} has not been implemented"
            )
        return visitor(self, node)

    @register_visitor(ast.Module)
    def visit_module(self, node: ast.Module) -> Iterable[T]:
        for statement in node.body:
            yield from self.visit(statement)
        for type_ignore in node.type_ignores:
            yield from self.visit(type_ignore)

    @register_visitor(ast.Interactive)
    def visit_interactive(self, node: ast.Interactive) -> Iterable[T]:
        for statement in node.body:
            yield from self.visit(statement)

    @register_visitor(ast.Expression)
    def visit_expression(self, node: ast.Expression) -> Iterable[T]:
        yield from self.visit(node.body)

    @register_visitor(ast.FunctionType)
    def visit_function_type(self, node: ast.FunctionType) -> Iterable[T]:
        for argtype in node.argtypes:
            yield from self.visit(argtype)
        yield from self.visit(node.returns)

    @register_visitor(ast.FunctionDef)
    def visit_function_def(self, node: ast.FunctionDef) -> Iterable[T]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        yield from self.visit(node.args)
        if node.returns is not None:
            yield from self.visit(node.returns)
        for statement in node.body:
            yield from self.visit(statement)

    @register_visitor(ast.AsyncFunctionDef)
    def visit_async_function_def(
        self, node: ast.AsyncFunctionDef
    ) -> Iterable[T]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        yield from self.visit(node.args)
        if node.returns is not None:
            yield from self.visit(node.returns)
        for statement in node.body:
            yield from self.visit(statement)

    @register_visitor(ast.ClassDef)
    def visit_class_def(self, node: ast.ClassDef) -> Iterable[T]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        for base in node.bases:
            yield from self.visit(base)
        for keyword in node.keywords:
            yield from self.visit(keyword)
        for statement in node.body:
            yield from self.visit(statement)

    @register_visitor(ast.Return)
    def visit_return(self, node: ast.Return) -> Iterable[T]:
        if node.value is not None:
            yield from self.visit(node.value)

    @register_visitor(ast.Delete)
    def visit_delete(self, node: ast.Delete) -> Iterable[T]:
        for target in node.targets:
            yield from self.visit(target)

    @register_visitor(ast.Assign)
    def visit_assign(self, node: ast.Assign) -> Iterable[T]:
        for target in node.targets:
            yield from self.visit(target)
        yield from self.visit(node.value)

    @register_visitor(ast.AugAssign)
    def visit_aug_assign(self, node: ast.AugAssign) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.value)

    @register_visitor(ast.AnnAssign)
    def visit_ann_assign(self, node: ast.AnnAssign) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.annotation)
        if node.value is not None:
            yield from self.visit(node.value)

    @register_visitor(ast.For)
    def visit_for(self, node: ast.For) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.iter)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    @register_visitor(ast.AsyncFor)
    def visit_async_for(self, node: ast.AsyncFor) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.iter)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    @register_visitor(ast.While)
    def visit_while(self, node: ast.While) -> Iterable[T]:
        yield from self.visit(node.test)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    @register_visitor(ast.If)
    def visit_if(self, node: ast.If) -> Iterable[T]:
        yield from self.visit(node.test)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    @register_visitor(ast.With)
    def visit_with(self, node: ast.With) -> Iterable[T]:
        for item in node.items:
            yield from self.visit(item)
        for statement in node.body:
            yield from self.visit(statement)

    @register_visitor(ast.AsyncWith)
    def visit_async_with(self, node: ast.AsyncWith) -> Iterable[T]:
        for item in node.items:
            yield from self.visit(item)
        for statement in node.body:
            yield from self.visit(statement)

    if sys.version_info >= (3, 10):

        @register_visitor(ast.Match)
        def visit_match(self, node: ast.Match) -> Iterable[T]:
            yield from self.visit(node.subject)
            for case in node.cases:
                yield from self.visit(case)

    @register_visitor(ast.Raise)
    def visit_raise(self, node: ast.Raise) -> Iterable[T]:
        if node.exc is not None:
            yield from self.visit(node.exc)
        if node.cause is not None:
            yield from self.visit(node.cause)

    @register_visitor(ast.Try)
    def visit_try(self, node: ast.Try) -> Iterable[T]:
        for statement in node.body:
            yield from self.visit(statement)
        for handler in node.handlers:
            yield from self.visit(handler)
        for statement in node.orelse:
            yield from self.visit(statement)
        for statement in node.finalbody:
            yield from self.visit(statement)

    @register_visitor(ast.Assert)
    def visit_assert(self, node: ast.Assert) -> Iterable[T]:
        yield from self.visit(node.test)
        if node.msg is not None:
            yield from self.visit(node.msg)

    @register_visitor(ast.Import)
    def visit_import(self, node: ast.Import) -> Iterable[T]:
        for name in node.names:
            yield from self.visit(name)

    @register_visitor(ast.ImportFrom)
    def visit_import_from(self, node: ast.ImportFrom) -> Iterable[T]:
        for name in node.names:
            yield from self.visit(name)

    @register_visitor(ast.Global)
    def visit_global(self, node: ast.Global) -> Iterable[T]:
        return ()

    @register_visitor(ast.Nonlocal)
    def visit_nonlocal(self, node: ast.Nonlocal) -> Iterable[T]:
        return ()

    @register_visitor(ast.Expr)
    def visit_expr(self, node: ast.Expr) -> Iterable[T]:
        yield from self.visit(node.value)

    @register_visitor(ast.Pass)
    def visit_pass(self, node: ast.Pass) -> Iterable[T]:
        return ()

    @register_visitor(ast.Break)
    def visit_break(self, node: ast.Break) -> Iterable[T]:
        return ()

    @register_visitor(ast.Continue)
    def visit_continue(self, node: ast.Continue) -> Iterable[T]:
        return ()

    @register_visitor(ast.BoolOp)
    def visit_bool_op(self, node: ast.BoolOp) -> Iterable[T]:
        for value in node.values:
            yield from self.visit(value)

    @register_visitor(ast.NamedExpr)
    def visit_named_expr(self, node: ast.NamedExpr) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.value)

    @register_visitor(ast.BinOp)
    def visit_bin_op(self, node: ast.BinOp) -> Iterable[T]:
        yield from self.visit(node.left)
        yield from self.visit(node.right)

    @register_visitor(ast.UnaryOp)
    def visit_unary_op(self, node: ast.UnaryOp) -> Iterable[T]:
        yield from self.visit(node.operand)

    @register_visitor(ast.Lambda)
    def visit_lambda(self, node: ast.Lambda) -> Iterable[T]:
        yield from self.visit(node.args)
        yield from self.visit(node.body)

    @register_visitor(ast.IfExp)
    def visit_if_exp(self, node: ast.IfExp) -> Iterable[T]:
        yield from self.visit(node.test)
        yield from self.visit(node.body)
        yield from self.visit(node.orelse)

    @register_visitor(ast.Dict)
    def visit_dict(self, node: ast.Dict) -> Iterable[T]:
        for key in node.keys:
            if key is not None:
                yield from self.visit(key)
        for value in node.values:
            yield from self.visit(value)

    @register_visitor(ast.Set)
    def visit_set(self, node: ast.Set) -> Iterable[T]:
        for elt in node.elts:
            yield from self.visit(elt)

    @register_visitor(ast.ListComp)
    def visit_list_comp(self, node: ast.ListComp) -> Iterable[T]:
        yield from self.visit(node.elt)
        for generator in node.generators:
            yield from self.visit(generator)

    @register_visitor(ast.SetComp)
    def visit_set_comp(self, node: ast.SetComp) -> Iterable[T]:
        yield from self.visit(node.elt)
        for generator in node.generators:
            yield from self.visit(generator)

    @register_visitor(ast.DictComp)
    def visit_dict_comp(self, node: ast.DictComp) -> Iterable[T]:
        yield from self.visit(node.key)
        yield from self.visit(node.value)
        for generator in node.generators:
            yield from self.visit(generator)

    @register_visitor(ast.GeneratorExp)
    def visit_generator_exp(self, node: ast.GeneratorExp) -> Iterable[T]:
        yield from self.visit(node.elt)
        for generator in node.generators:
            yield from self.visit(generator)

    @register_visitor(ast.Await)
    def visit_await(self, node: ast.Await) -> Iterable[T]:
        yield from self.visit(node.value)

    @register_visitor(ast.Yield)
    def visit_yield(self, node: ast.Yield) -> Iterable[T]:
        if node.value is not None:
            yield from self.visit(node.value)

    @register_visitor(ast.YieldFrom)
    def visit_yield_from(self, node: ast.YieldFrom) -> Iterable[T]:
        yield from self.visit(node.value)

    @register_visitor(ast.Compare)
    def visit_compare(self, node: ast.Compare) -> Iterable[T]:
        yield from self.visit(node.left)
        for comparator in node.comparators:
            yield from self.visit(comparator)

    @register_visitor(ast.Call)
    def visit_call(self, node: ast.Call) -> Iterable[T]:
        yield from self.visit(node.func)
        for arg in node.args:
            yield from self.visit(arg)
        for keyword in node.keywords:
            yield from self.visit(keyword)

    @register_visitor(ast.FormattedValue)
    def visit_formatted_value(self, node: ast.FormattedValue) -> Iterable[T]:
        yield from self.visit(node.value)
        if node.format_spec is not None:
            yield from self.visit(node.format_spec)

    @register_visitor(ast.JoinedStr)
    def visit_joined_str(self, node: ast.JoinedStr) -> Iterable[T]:
        for value in node.values:
            yield from self.visit(value)

    @register_visitor(ast.Constant)
    def visit_constant(self, node: ast.Constant) -> Iterable[T]:
        return ()

    @register_visitor(ast.Attribute)
    def visit_attribute(self, node: ast.Attribute) -> Iterable[T]:
        yield from self.visit(node.value)

    @register_visitor(ast.Subscript)
    def visit_subscript(self, node: ast.Subscript) -> Iterable[T]:
        yield from self.visit(node.value)
        yield from self.visit(node.slice)

    @register_visitor(ast.Starred)
    def visit_starred(self, node: ast.Starred) -> Iterable[T]:
        yield from self.visit(node.value)

    @register_visitor(ast.Name)
    def visit_name(self, node: ast.Name) -> Iterable[T]:
        return ()

    @register_visitor(ast.List)
    def visit_list(self, node: ast.List) -> Iterable[T]:
        for elt in node.elts:
            yield from self.visit(elt)

    @register_visitor(ast.Tuple)
    def visit_tuple(self, node: ast.Tuple) -> Iterable[T]:
        for elt in node.elts:
            yield from self.visit(elt)

    @register_visitor(ast.Slice)
    def visit_slice(self, node: ast.Slice) -> Iterable[T]:
        if node.lower is not None:
            yield from self.visit(node.lower)
        if node.upper is not None:
            yield from self.visit(node.upper)
        if node.step is not None:
            yield from self.visit(node.step)

    if sys.version_info < (3, 9):

        @register_visitor(ast.ExtSlice)
        def visit_ext_slice(self, node: ast.ExtSlice) -> Iterable[T]:
            for dim in node.dims:
                yield from self.visit(dim)

        @register_visitor(ast.Index)
        def visit_index(self, node: ast.Index) -> Iterable[T]:
            yield from self.visit(node.value)

    @register_visitor(ast.comprehension)
    def visit_comprehension(self, node: ast.comprehension) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.iter)
        for ifs in node.ifs:
            yield from self.visit(ifs)

    @register_visitor(ast.ExceptHandler)
    def visit_except_handler(self, node: ast.ExceptHandler) -> Iterable[T]:
        if node.type is not None:
            yield from self.visit(node.type)
        for statement in node.body:
            yield from self.visit(statement)

    @register_visitor(ast.arguments)
    def visit_arguments(self, node: ast.arguments) -> Iterable[T]:
        for arg in node.posonlyargs:
            yield from self.visit(arg)
        for arg in node.args:
            yield from self.visit(arg)
        if node.vararg is not None:
            yield from self.visit(node.vararg)
        for arg in node.kwonlyargs:
            yield from self.visit(arg)
        for default in node.kw_defaults:
            if default is not None:
                yield from self.visit(default)
        if node.kwarg is not None:
            yield from self.visit(node.kwarg)
        for default in node.defaults:
            yield from self.visit(default)

    @register_visitor(ast.arg)
    def visit_arg(self, node: ast.arg) -> Iterable[T]:
        if node.annotation is not None:
            yield from self.visit(node.annotation)

    @register_visitor(ast.keyword)
    def visit_keyword(self, node: ast.keyword) -> Iterable[T]:
        yield from self.visit(node.value)

    @register_visitor(ast.alias)
    def visit_alias(self, node: ast.alias) -> Iterable[T]:
        return ()

    @register_visitor(ast.withitem)
    def visit_withitem(self, node: ast.withitem) -> Iterable[T]:
        yield from self.visit(node.context_expr)
        if node.optional_vars is not None:
            yield from self.visit(node.optional_vars)

    if sys.version_info >= (3, 10):

        @register_visitor(ast.match_case)
        def visit_match_case(self, node: ast.match_case) -> Iterable[T]:
            yield from self.visit(node.pattern)
            if node.guard is not None:
                yield from self.visit(node.guard)
            for statement in node.body:
                yield from self.visit(statement)

        @register_visitor(ast.MatchValue)
        def visit_match_value(self, node: ast.MatchValue) -> Iterable[T]:
            yield from self.visit(node.value)

        @register_visitor(ast.MatchSingleton)
        def visit_match_singleton(
            self, node: ast.MatchSingleton
        ) -> Iterable[T]:
            return ()

        @register_visitor(ast.MatchSequence)
        def visit_match_sequence(self, node: ast.MatchSequence) -> Iterable[T]:
            for pattern in node.patterns:
                yield from self.visit(pattern)

        @register_visitor(ast.MatchMapping)
        def visit_match_mapping(self, node: ast.MatchMapping) -> Iterable[T]:
            for key in node.keys:
                yield from self.visit(key)
            for pattern in node.patterns:
                yield from self.visit(pattern)

        @register_visitor(ast.MatchClass)
        def visit_match_class(self, node: ast.MatchClass) -> Iterable[T]:
            yield from self.visit(node.cls)
            for pattern in node.patterns:
                yield from self.visit(pattern)
            for kwd_pattern in node.kwd_patterns:
                yield from self.visit(kwd_pattern)

        @register_visitor(ast.MatchStar)
        def visit_match_star(self, node: ast.MatchStar) -> Iterable[T]:
            return ()

        @register_visitor(ast.MatchAs)
        def visit_match_as(self, node: ast.MatchAs) -> Iterable[T]:
            if node.pattern is not None:
                yield from self.visit(node.pattern)

        @register_visitor(ast.MatchOr)
        def visit_match_or(self, node: ast.MatchOr) -> Iterable[T]:
            for pattern in node.patterns:
                yield from self.visit(pattern)

    @register_visitor(ast.type_ignore)
    def visit_type_ignore(self, node: ast.type_ignore) -> Iterable[T]:
        return ()


NodeVisitor._find_visitor_methods()
