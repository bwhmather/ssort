import ast
import dataclasses
import enum
import functools
import sys

from ssort._bindings import get_bindings
from ssort._builtins import CLASS_BUILTINS


class Scope(enum.Enum):
    LOCAL = "LOCAL"
    NONLOCAL = "NONLOCAL"
    GLOBAL = "GLOBAL"


@dataclasses.dataclass(frozen=True)
class Requirement:
    name: str
    lineno: int
    col_offset: int
    deferred: bool = False
    scope: Scope = Scope.LOCAL


@functools.singledispatch
def get_requirements(node):
    raise NotImplementedError(
        f"could not find requirements for unsupported node:  {node!r}"
        f"at line {node.lineno}, column: {node.col_offset}"
    )


def _get_scope_from_arguments(args):
    scope = set()
    scope.update(arg.arg for arg in args.posonlyargs)
    scope.update(arg.arg for arg in args.args)  # Arghhh.
    if args.vararg:
        scope.add(args.vararg.arg)
    scope.update(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        scope.add(args.kwarg.arg)
    return scope


@get_requirements.register(ast.FunctionDef)
@get_requirements.register(ast.AsyncFunctionDef)
def _get_requirements_for_function_def(node):
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
    for decorator in node.decorator_list:
        yield from get_requirements(decorator)

    scope = _get_scope_from_arguments(node.args)

    requirements = []
    for statement in node.body:
        scope.update(get_bindings(statement))
        for requirement in get_requirements(statement):
            if not requirement.deferred:
                requirement = dataclasses.replace(requirement, deferred=True)
            requirements.append(requirement)

    for requirement in requirements:
        if requirement.scope == Scope.GLOBAL:
            yield requirement

        elif requirement.scope == Scope.NONLOCAL:
            yield dataclasses.replace(requirement, scope=Scope.LOCAL)

        else:
            if requirement.name not in scope:
                yield requirement


@get_requirements.register(ast.ClassDef)
def _get_requirements_for_class_def(node):
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
    for decorator in node.decorator_list:
        yield from get_requirements(decorator)

    for base in node.bases:
        yield from get_requirements(base)

    scope = set(CLASS_BUILTINS)

    for statement in node.body:
        for stmt_dep in get_requirements(statement):
            if stmt_dep.deferred or stmt_dep.name not in scope:
                yield stmt_dep

        scope.update(get_bindings(statement))


@get_requirements.register(ast.Return)
def _get_requirements_for_return(node):
    """
    ..code:: python

        Return(expr? value)

    """
    if node.value:
        yield from get_requirements(node.value)


@get_requirements.register(ast.Delete)
def _get_requirements_for_delete(node):
    """
    ..code:: python

        Delete(expr* targets)
    """
    for target in node.targets:
        yield from get_requirements(target)


@get_requirements.register(ast.Assign)
def _get_requirements_for_assign(node):
    """
    ..code:: python

        Assign(expr* targets, expr value, string? type_comment)
    """
    yield from get_requirements(node.value)


@get_requirements.register(ast.AugAssign)
def _get_requirements_for_aug_assign(node):
    """
    ..code:: python

        AugAssign(expr target, operator op, expr value)
    """
    yield from get_requirements(node.value)


@get_requirements.register(ast.AnnAssign)
def _get_requirements_for_ann_assign(node):
    """
    ..code:: python

        # 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)

    """
    # Can be None for type declaration.
    if node.value:
        yield from get_requirements(node.value)


@get_requirements.register(ast.For)
@get_requirements.register(ast.AsyncFor)
def _get_requirements_for_for(node):
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
    bindings = set(get_bindings(node))

    yield from get_requirements(node.iter)

    for stmt in node.body:
        for requirement in get_requirements(stmt):
            if requirement.name not in bindings:
                yield requirement

    for stmt in node.orelse:
        for requirement in get_requirements(stmt):
            if requirement.name not in bindings:
                yield requirement


@get_requirements.register(ast.While)
def _get_requirements_for_while(node):
    """
    ..code:: python

        While(expr test, stmt* body, stmt* orelse)
    """
    yield from get_requirements(node.test)

    for stmt in node.body:
        yield from get_requirements(stmt)

    for stmt in node.orelse:
        yield from get_requirements(stmt)


@get_requirements.register(ast.If)
def _get_requirements_for_if(node):
    """
    ..code:: python

        If(expr test, stmt* body, stmt* orelse)
    """
    yield from get_requirements(node.test)

    for stmt in node.body:
        yield from get_requirements(stmt)

    for stmt in node.orelse:
        yield from get_requirements(stmt)


@get_requirements.register(ast.With)
@get_requirements.register(ast.AsyncWith)
def _get_requirements_for_with(node):
    """
    ..code:: python

        With(withitem* items, stmt* body, string? type_comment)

    ..code:: python

        AsyncWith(withitem* items, stmt* body, string? type_comment)

    .. code:: python

        WithItem(expr context_expr, expr? optional_vars)
    """
    bindings = set(get_bindings(node))

    for item in node.items:
        yield from get_requirements(item.context_expr)

    for stmt in node.body:
        for requirement in get_requirements(stmt):
            if requirement.name not in bindings:
                yield requirement


@get_requirements.register(ast.Raise)
def _get_requirements_for_raise(node):
    """
    ..code:: python

        Raise(expr? exc, expr? cause)
    """
    if node.exc:
        yield from get_requirements(node.exc)

    if node.cause:
        yield from get_requirements(node.cause)


@get_requirements.register(ast.Try)
def _get_requirements_for_try(node):
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
    for stmt in node.body:
        yield from get_requirements(stmt)

    for handler in node.handlers:
        if handler.type:
            yield from get_requirements(handler.type)

        for stmt in handler.body:
            yield from get_requirements(stmt)

    for stmt in node.orelse:
        yield from get_requirements(stmt)

    for stmt in node.finalbody:
        yield from get_requirements(stmt)


@get_requirements.register(ast.Assert)
def _get_requirements_for_assert(node):
    """
    ..code:: python

        Assert(expr test, expr? msg)

    """
    yield from get_requirements(node.test)

    if node.msg:
        yield from get_requirements(node.msg)


@get_requirements.register(ast.Import)
def _get_requirements_for_import(node):
    """
    ..code:: python

        Import(alias* names)
    """
    return
    yield


@get_requirements.register(ast.ImportFrom)
def _get_requirements_for_import_from(node):
    """
    ..code:: python

        ImportFrom(identifier? module, alias* names, int? level)

    """
    return
    yield


@get_requirements.register(ast.Global)
def _get_requirements_for_global(node):
    """
    ..code:: python

        Global(identifier* names)
    """
    for name in node.names:
        yield Requirement(
            name=name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            scope=Scope.GLOBAL,
        )


@get_requirements.register(ast.Nonlocal)
def _get_requirements_for_non_local(node):
    """
    ..code:: python

        Nonlocal(identifier* names)
    """
    for name in node.names:
        yield Requirement(
            name=name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            scope=Scope.NONLOCAL,
        )


@get_requirements.register(ast.Expr)
def _get_requirements_for_expr(node):
    """
    ..code:: python

        Expr(expr value)
    """
    yield from get_requirements(node.value)


@get_requirements.register(ast.Pass)
@get_requirements.register(ast.Break)
@get_requirements.register(ast.Continue)
def _get_requirements_for_control_flow(node):
    """
    ..code:: python

        Pass | Break | Continue

    """
    return
    yield


@get_requirements.register(ast.BoolOp)
def _get_requirements_for_bool_op(node):
    """
    ..code:: python

        # BoolOp() can use left & right?
        # expr
        BoolOp(boolop op, expr* values)
    """
    for value in node.values:
        yield from get_requirements(value)


@get_requirements.register(ast.NamedExpr)
def _get_requirements_for_named_expr(node):
    """
    ..code:: python

        NamedExpr(expr target, expr value)
    """
    raise NotImplementedError("TODO")


@get_requirements.register(ast.BinOp)
def _get_requirements_for_bin_op(node):

    """
    ..code:: python

        BinOp(expr left, operator op, expr right)
    """
    yield from get_requirements(node.left)
    yield from get_requirements(node.right)


@get_requirements.register(ast.UnaryOp)
def _get_requirements_for_unary_op(node):
    """
    ..code:: python

        UnaryOp(unaryop op, expr operand)
    """

    yield from get_requirements(node.operand)


@get_requirements.register(ast.Lambda)
def _get_requirements_for_lambda(node):
    """
    ..code:: python

        Lambda(arguments args, expr body)
    """
    scope = _get_scope_from_arguments(node.args)
    for requirement in get_requirements(node.body):
        if requirement.name not in scope:
            yield requirement


@get_requirements.register(ast.IfExp)
def _get_requirements_for_if_exp(node):
    """
    ..code:: python

        IfExp(expr test, expr body, expr orelse)
    """
    yield from get_requirements(node.test)
    yield from get_requirements(node.body)
    yield from get_requirements(node.orelse)


@get_requirements.register(ast.Dict)
def _get_requirements_for_dict(node):
    """
    ..code:: python

        Dict(expr* keys, expr* values)
    """
    for key, value in zip(node.keys, node.values):
        yield from get_requirements(value)


@get_requirements.register(ast.Set)
def _get_requirements_for_set(node):
    """
    ..code:: python

        Set(expr* elts)
    """
    for elt in node.elts:
        yield from get_requirements(elt)


@get_requirements.register(ast.ListComp)
def _get_requirements_for_list_comp(node):
    """
    ..code:: python

        ListComp(expr elt, comprehension* generators)
    """
    requirements = []
    requirements += get_requirements(node.elt)

    for generator in node.generators:
        requirements += get_requirements(generator.iter)

        for if_expr in generator.ifs:
            requirements += get_requirements(if_expr)

    bindings = set(get_bindings(node))

    for requirement in requirements:
        if requirement.name not in bindings:
            yield requirement


@get_requirements.register(ast.SetComp)
def _get_requirements_for_set_comp(node):
    """
    ..code:: python

        SetComp(expr elt, comprehension* generators)
    """
    requirements = []
    requirements += get_requirements(node.elt)

    for generator in node.generators:
        requirements += get_requirements(generator.iter)

        for if_expr in generator.ifs:
            requirements += get_requirements(if_expr)

    bindings = set(get_bindings(node))

    for requirement in requirements:
        if requirement.name not in bindings:
            yield requirement


@get_requirements.register(ast.DictComp)
def _get_requirements_for_dict_comp(node):
    """
    ..code:: python

        DictComp(expr key, expr value, comprehension* generators)
    """
    requirements = []
    requirements += get_requirements(node.key)
    requirements += get_requirements(node.value)

    for generator in node.generators:
        requirements += get_requirements(generator.iter)

        for if_expr in generator.ifs:
            requirements += get_requirements(if_expr)

    bindings = set(get_bindings(node))

    for requirement in requirements:
        if requirement.name not in bindings:
            yield requirement


@get_requirements.register(ast.GeneratorExp)
def _get_requirements_for_generator_exp(node):
    """
    ..code:: python

        GeneratorExp(expr elt, comprehension* generators)
    """
    requirements = []
    requirements += get_requirements(node.elt)

    for generator in node.generators:
        requirements += get_requirements(generator.iter)

        for if_expr in generator.ifs:
            requirements += get_requirements(if_expr)

    bindings = set(get_bindings(node))

    for requirement in requirements:
        if requirement.name not in bindings:
            yield requirement


@get_requirements.register(ast.Await)
def _get_requirements_for_await(node):
    """
    ..code:: python

        # the grammar constrains where yield expressions can occur
        Await(expr value)
    """
    yield from get_requirements(node.value)


@get_requirements.register(ast.Yield)
def _get_requirements_for_yield(node):
    """
    ..code:: python

        Yield(expr? value)
    """
    if node.value:
        yield from get_requirements(node.value)


@get_requirements.register(ast.YieldFrom)
def _get_requirements_for_yield_from(node):
    """
    ..code:: python

        YieldFrom(expr value)
    """
    yield from get_requirements(node.value)


@get_requirements.register(ast.Compare)
def _get_requirements_for_compare(node):
    """
    ..code:: python

        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        Compare(expr left, cmpop* ops, expr* comparators)
    """
    yield from get_requirements(node.left)

    for comp in node.comparators:
        yield from get_requirements(comp)


@get_requirements.register(ast.Call)
def _get_requirements_for_call(node):
    """
    ..code:: python

        Call(expr func, expr* args, keyword* keywords)
    """
    yield from get_requirements(node.func)

    for arg in node.args:
        yield from get_requirements(arg)

    for kwarg in node.keywords:
        yield from get_requirements(kwarg.value)


@get_requirements.register(ast.FormattedValue)
def _get_requirements_for_formatted_value(node):
    """
    ..code:: python

        FormattedValue(expr value, int? conversion, expr? format_spec)
    """
    yield from get_requirements(node.value)


@get_requirements.register(ast.JoinedStr)
def _get_requirements_for_joined_str(node):
    """
    ..code:: python

        JoinedStr(expr* values)
    """
    return
    yield


@get_requirements.register(ast.Constant)
def _get_requirements_for_constant(node):
    """
    ..code:: python

        Constant(constant value, string? kind)
    """
    return
    yield


@get_requirements.register(ast.Attribute)
def _get_requirements_for_attribute(node):
    """
    ..code:: python

        # the following expression can appear in assignment context
        Attribute(expr value, identifier attr, expr_context ctx)
    """
    assert isinstance(node.ctx, (ast.Load, ast.Del))
    yield from get_requirements(node.value)


@get_requirements.register(ast.Subscript)
def _get_requirements_for_subscript(node):
    """
    ..code:: python

        Subscript(expr value, expr slice, expr_context ctx)
    """
    assert isinstance(node.ctx, (ast.Load, ast.Del))
    yield from get_requirements(node.value)
    yield from get_requirements(node.slice)


@get_requirements.register(ast.Starred)
def _get_requirements_for_starred(node):
    """
    ..code:: python

        Starred(expr value, expr_context ctx)
    """
    assert isinstance(node.ctx, (ast.Load, ast.Del))
    yield from get_requirements(node.value)


@get_requirements.register(ast.Name)
def _get_requirements_for_name(node):

    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    assert isinstance(node.ctx, (ast.Load, ast.Del))
    yield Requirement(
        name=node.id, lineno=node.lineno, col_offset=node.col_offset
    )


@get_requirements.register(ast.List)
def _get_requirements_for_list(node):

    """
    ..code:: python

        List(expr* elts, expr_context ctx)
    """
    assert isinstance(node.ctx, (ast.Load, ast.Del))
    for element in node.elts:
        yield from get_requirements(element)


@get_requirements.register(ast.Tuple)
def _get_requirements_for_tuple(node):
    """
    ..code:: python

        Tuple(expr* elts, expr_context ctx)

    """
    assert isinstance(node.ctx, (ast.Load, ast.Del))
    for element in node.elts:
        yield from get_requirements(element)


@get_requirements.register(ast.Slice)
def _get_requirements_for_slice(node):
    """
    ..code:: python

        # can appear only in Subscript
        Slice(expr? lower, expr? upper, expr? step)

    """
    if node.lower is not None:
        yield from get_requirements(node.lower)

    if node.upper is not None:
        yield from get_requirements(node.upper)

    if node.step is not None:
        yield from get_requirements(node.step)


if sys.version_info < (3, 9):

    @get_requirements.register(ast.Index)
    def _get_requirements_for_index(node):
        """
        ..code:: python

            # can appear only in Subscript
            Index(expr value)
        """
        yield from get_requirements(node.value)
