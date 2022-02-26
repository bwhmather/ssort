import ast
import dataclasses
import enum

from ssort._bindings import get_bindings
from ssort._builtins import CLASS_BUILTINS
from ssort._visitor import node_visitor


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


@node_visitor
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


@get_requirements.register(ast.Name)
def _get_requirements_for_name(node):
    """
    ..code:: python

        Name(identifier id, expr_context ctx)
    """
    if isinstance(node.ctx, (ast.Load, ast.Del)):
        yield Requirement(
            name=node.id, lineno=node.lineno, col_offset=node.col_offset
        )
