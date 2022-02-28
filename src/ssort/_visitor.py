from __future__ import annotations

import ast
import inspect
import sys
from typing import Callable, Generic, Iterable, TypeVar

T = TypeVar("T")


class NodeVisitor(Generic[T]):
    """A high performance AST node visitor.

    Provides an interface similar to `ast.NodeVisitor` but is much more
    performant.
    """

    _visitors: dict[type, Callable[[NodeVisitor, ast.AST], Iterable[T]]] = {}

    @classmethod
    def _find_visitor_methods(cls):
        # Register visitor methods according to their type annotations.
        cls._visitors = {}
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith("visit_"):
                continue

            signature = inspect.signature(func)
            parameters = list(signature.parameters.values())

            # All visitor signatures should be of form (self, node)
            if len(parameters) != 2:
                raise ValueError(f"Invalid signature for visitor: {name!r}")

            annotation = parameters[1].annotation
            if not isinstance(annotation, str):
                raise ValueError(
                    f"Non-string annotation for visitor: {name!r}"
                )

            # Process each type in a union.
            for type_name in annotation.split("|"):
                type_name = type_name.strip()
                try:
                    ast_type = eval(type_name)
                except Exception:
                    raise ValueError(
                        f"Unable to parse visitor annotation: {annotation}"
                    )
                cls._visitors[ast_type] = func

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

    def visit_module(self, node: ast.Module) -> Iterable[T]:
        for statement in node.body:
            yield from self.visit(statement)
        for type_ignore in node.type_ignores:
            yield from self.visit(type_ignore)

    def visit_interactive(self, node: ast.Interactive) -> Iterable[T]:
        for statement in node.body:
            yield from self.visit(statement)

    def visit_expression(self, node: ast.Expression) -> Iterable[T]:
        yield from self.visit(node.body)

    def visit_function_type(self, node: ast.FunctionType) -> Iterable[T]:
        for argtype in node.argtypes:
            yield from self.visit(argtype)
        yield from self.visit(node.returns)

    def visit_function_def(self, node: ast.FunctionDef) -> Iterable[T]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        yield from self.visit(node.args)
        if node.returns is not None:
            yield from self.visit(node.returns)
        for statement in node.body:
            yield from self.visit(statement)

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

    def visit_class_def(self, node: ast.ClassDef) -> Iterable[T]:
        for decorator in node.decorator_list:
            yield from self.visit(decorator)
        for base in node.bases:
            yield from self.visit(base)
        for keyword in node.keywords:
            yield from self.visit(keyword)
        for statement in node.body:
            yield from self.visit(statement)

    def visit_return(self, node: ast.Return) -> Iterable[T]:
        if node.value is not None:
            yield from self.visit(node.value)

    def visit_delete(self, node: ast.Delete) -> Iterable[T]:
        for target in node.targets:
            yield from self.visit(target)

    def visit_assign(self, node: ast.Assign) -> Iterable[T]:
        for target in node.targets:
            yield from self.visit(target)
        yield from self.visit(node.value)

    def visit_aug_assign(self, node: ast.AugAssign) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.value)

    def visit_ann_assign(self, node: ast.AnnAssign) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.annotation)
        if node.value is not None:
            yield from self.visit(node.value)

    def visit_for(self, node: ast.For) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.iter)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    def visit_async_for(self, node: ast.AsyncFor) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.iter)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    def visit_while(self, node: ast.While) -> Iterable[T]:
        yield from self.visit(node.test)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    def visit_if(self, node: ast.If) -> Iterable[T]:
        yield from self.visit(node.test)
        for statement in node.body:
            yield from self.visit(statement)
        for statement in node.orelse:
            yield from self.visit(statement)

    def visit_with(self, node: ast.With) -> Iterable[T]:
        for item in node.items:
            yield from self.visit(item)
        for statement in node.body:
            yield from self.visit(statement)

    def visit_async_with(self, node: ast.AsyncWith) -> Iterable[T]:
        for item in node.items:
            yield from self.visit(item)
        for statement in node.body:
            yield from self.visit(statement)

    if sys.version_info >= (3, 10):

        def visit_match(self, node: ast.Match) -> Iterable[T]:
            yield from self.visit(node.subject)
            for case in node.cases:
                yield from self.visit(case)

    def visit_raise(self, node: ast.Raise) -> Iterable[T]:
        if node.exc is not None:
            yield from self.visit(node.exc)
        if node.cause is not None:
            yield from self.visit(node.cause)

    def visit_try(self, node: ast.Try) -> Iterable[T]:
        for statement in node.body:
            yield from self.visit(statement)
        for handler in node.handlers:
            yield from self.visit(handler)
        for statement in node.orelse:
            yield from self.visit(statement)
        for statement in node.finalbody:
            yield from self.visit(statement)

    def visit_assert(self, node: ast.Assert) -> Iterable[T]:
        yield from self.visit(node.test)
        if node.msg is not None:
            yield from self.visit(node.msg)

    def visit_import(self, node: ast.Import) -> Iterable[T]:
        for name in node.names:
            yield from self.visit(name)

    def visit_import_from(self, node: ast.ImportFrom) -> Iterable[T]:
        for name in node.names:
            yield from self.visit(name)

    def visit_global(self, node: ast.Global) -> Iterable[T]:
        return ()

    def visit_nonlocal(self, node: ast.Nonlocal) -> Iterable[T]:
        return ()

    def visit_expr(self, node: ast.Expr) -> Iterable[T]:
        yield from self.visit(node.value)

    def visit_pass(self, node: ast.Pass) -> Iterable[T]:
        return ()

    def visit_break(self, node: ast.Break) -> Iterable[T]:
        return ()

    def visit_continue(self, node: ast.Continue) -> Iterable[T]:
        return ()

    def visit_bool_op(self, node: ast.BoolOp) -> Iterable[T]:
        for value in node.values:
            yield from self.visit(value)

    def visit_named_expr(self, node: ast.NamedExpr) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.value)

    def visit_bin_op(self, node: ast.BinOp) -> Iterable[T]:
        yield from self.visit(node.left)
        yield from self.visit(node.right)

    def visit_unary_op(self, node: ast.UnaryOp) -> Iterable[T]:
        yield from self.visit(node.operand)

    def visit_lambda(self, node: ast.Lambda) -> Iterable[T]:
        yield from self.visit(node.args)
        yield from self.visit(node.body)

    def visit_if_exp(self, node: ast.IfExp) -> Iterable[T]:
        yield from self.visit(node.test)
        yield from self.visit(node.body)
        yield from self.visit(node.orelse)

    def visit_dict(self, node: ast.Dict) -> Iterable[T]:
        for key in node.keys:
            if key is not None:
                yield from self.visit(key)
        for value in node.values:
            yield from self.visit(value)

    def visit_set(self, node: ast.Set) -> Iterable[T]:
        for elt in node.elts:
            yield from self.visit(elt)

    def visit_list_comp(self, node: ast.ListComp) -> Iterable[T]:
        yield from self.visit(node.elt)
        for generator in node.generators:
            yield from self.visit(generator)

    def visit_set_comp(self, node: ast.SetComp) -> Iterable[T]:
        yield from self.visit(node.elt)
        for generator in node.generators:
            yield from self.visit(generator)

    def visit_dict_comp(self, node: ast.DictComp) -> Iterable[T]:
        yield from self.visit(node.key)
        yield from self.visit(node.value)
        for generator in node.generators:
            yield from self.visit(generator)

    def visit_generator_exp(self, node: ast.GeneratorExp) -> Iterable[T]:
        yield from self.visit(node.elt)
        for generator in node.generators:
            yield from self.visit(generator)

    def visit_await(self, node: ast.Await) -> Iterable[T]:
        yield from self.visit(node.value)

    def visit_yield(self, node: ast.Yield) -> Iterable[T]:
        if node.value is not None:
            yield from self.visit(node.value)

    def visit_yield_from(self, node: ast.YieldFrom) -> Iterable[T]:
        yield from self.visit(node.value)

    def visit_compare(self, node: ast.Compare) -> Iterable[T]:
        yield from self.visit(node.left)
        for comparator in node.comparators:
            yield from self.visit(comparator)

    def visit_call(self, node: ast.Call) -> Iterable[T]:
        yield from self.visit(node.func)
        for arg in node.args:
            yield from self.visit(arg)
        for keyword in node.keywords:
            yield from self.visit(keyword)

    def visit_formatted_value(self, node: ast.FormattedValue) -> Iterable[T]:
        yield from self.visit(node.value)
        if node.format_spec is not None:
            yield from self.visit(node.format_spec)

    def visit_joined_str(self, node: ast.JoinedStr) -> Iterable[T]:
        for value in node.values:
            yield from self.visit(value)

    def visit_constant(self, node: ast.Constant) -> Iterable[T]:
        return ()

    def visit_attribute(self, node: ast.Attribute) -> Iterable[T]:
        yield from self.visit(node.value)

    def visit_subscript(self, node: ast.Subscript) -> Iterable[T]:
        yield from self.visit(node.value)
        yield from self.visit(node.slice)

    def visit_starred(self, node: ast.Starred) -> Iterable[T]:
        yield from self.visit(node.value)

    def visit_name(self, node: ast.Name) -> Iterable[T]:
        return ()

    def visit_list(self, node: ast.List) -> Iterable[T]:
        for elt in node.elts:
            yield from self.visit(elt)

    def visit_tuple(self, node: ast.Tuple) -> Iterable[T]:
        for elt in node.elts:
            yield from self.visit(elt)

    def visit_slice(self, node: ast.Slice) -> Iterable[T]:
        if node.lower is not None:
            yield from self.visit(node.lower)
        if node.upper is not None:
            yield from self.visit(node.upper)
        if node.step is not None:
            yield from self.visit(node.step)

    if sys.version_info < (3, 9):

        def visit_ext_slice(self, node: ast.ExtSlice) -> Iterable[T]:
            for dim in node.dims:
                yield from self.visit(dim)

        def visit_index(self, node: ast.Index) -> Iterable[T]:
            yield from self.visit(node.value)

    def visit_comprehension(self, node: ast.comprehension) -> Iterable[T]:
        yield from self.visit(node.target)
        yield from self.visit(node.iter)
        for ifs in node.ifs:
            yield from self.visit(ifs)

    def visit_except_handler(self, node: ast.ExceptHandler) -> Iterable[T]:
        if node.type is not None:
            yield from self.visit(node.type)
        for statement in node.body:
            yield from self.visit(statement)

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

    def visit_arg(self, node: ast.arg) -> Iterable[T]:
        if node.annotation is not None:
            yield from self.visit(node.annotation)

    def visit_keyword(self, node: ast.keyword) -> Iterable[T]:
        yield from self.visit(node.value)

    def visit_alias(self, node: ast.alias) -> Iterable[T]:
        return ()

    def visit_withitem(self, node: ast.withitem) -> Iterable[T]:
        yield from self.visit(node.context_expr)
        if node.optional_vars is not None:
            yield from self.visit(node.optional_vars)

    if sys.version_info >= (3, 10):

        def visit_match_case(self, node: ast.match_case) -> Iterable[T]:
            yield from self.visit(node.pattern)
            if node.guard is not None:
                yield from self.visit(node.guard)
            for statement in node.body:
                yield from self.visit(statement)

        def visit_match_value(self, node: ast.MatchValue) -> Iterable[T]:
            yield from self.visit(node.value)

        def visit_match_singleton(
            self, node: ast.MatchSingleton
        ) -> Iterable[T]:
            return ()

        def visit_match_sequence(self, node: ast.MatchSequence) -> Iterable[T]:
            for pattern in node.patterns:
                yield from self.visit(pattern)

        def visit_match_mapping(self, node: ast.MatchMapping) -> Iterable[T]:
            for key in node.keys:
                yield from self.visit(key)
            for pattern in node.patterns:
                yield from self.visit(pattern)

        def visit_match_class(self, node: ast.MatchClass) -> Iterable[T]:
            yield from self.visit(node.cls)
            for pattern in node.patterns:
                yield from self.visit(pattern)
            for kwd_pattern in node.kwd_patterns:
                yield from self.visit(kwd_pattern)

        def visit_match_star(self, node: ast.MatchStar) -> Iterable[T]:
            return ()

        def visit_match_as(self, node: ast.MatchAs) -> Iterable[T]:
            if node.pattern is not None:
                yield from self.visit(node.pattern)

        def visit_match_or(self, node: ast.MatchOr) -> Iterable[T]:
            for pattern in node.patterns:
                yield from self.visit(pattern)

    def visit_type_ignore(self, node: ast.type_ignore) -> Iterable[T]:
        return ()
