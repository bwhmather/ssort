import sys

from ssort._builtins import MODULE_BUILTINS
from ssort._graphs import Graph
from ssort._statements import (
    statement_bindings,
    statement_method_requirements,
    statement_requirements,
)


class ResolutionError(Exception):
    def __init__(self, msg, *, lineno, col_offset, name):
        super().__init__(msg)
        self.lineno = lineno
        self.col_offset = col_offset
        self.name = name


def statements_graph(statements):
    """
    Returns a dictionary mapping from statements to lists of other statements.
    """
    # A dictionary mapping from names to the statements which bind them.
    scope = {}

    unresolved = set()
    resolved = {}

    for statement in statements:
        for requirement in statement_requirements(statement):
            # TODO error if requirement is not deferred.
            if requirement.name in scope:
                resolved[requirement] = scope[requirement.name]
                continue

            if requirement.name in MODULE_BUILTINS:
                resolved[requirement] = None
                continue

            unresolved.add(requirement)

        for name in statement_bindings(statement):
            scope[name] = statement

    # Patch up dependencies that couldn't be resolved immediately.
    for requirement in list(unresolved):
        if requirement.name in scope:
            resolved[requirement] = scope[requirement.name]
            unresolved.remove(requirement)

    if "*" in scope:
        sys.stderr.write("WARNING: can't determine dependencies on * import\n")

        for requirement in unresolved:
            resolved[requirement] = scope["*"]

    else:
        for requirement in unresolved:
            raise ResolutionError(
                f"Could not resolve requirement {requirement.name!r}",
                name=requirement.name,
                lineno=requirement.lineno,
                col_offset=requirement.col_offset,
            )

    graph = Graph()
    for statement in statements:
        graph.add_node(statement)

    for statement in statements:
        for requirement in statement_requirements(statement):
            if resolved[requirement] is not None:
                graph.add_dependency(statement, resolved[requirement])

    return graph


def class_statements_initialisation_graph(statements):
    scope = {}

    graph = Graph()

    for statement in statements:
        graph.add_node(statement)

        for requirement in statement_requirements(statement):
            if requirement.deferred:
                continue

            if requirement.name not in scope:
                continue

            graph.add_dependency(statement, scope[requirement.name])

        for name in statement_bindings(statement):
            scope[name] = statement

    return graph


def class_statements_runtime_graph(statements):
    scope = {}

    graph = Graph()

    for statement in statements:
        graph.add_node(statement)

        for name in statement_bindings(statement):
            scope[name] = statement

    for statement in statements:
        for name in statement_method_requirements(statement):
            if name in scope:
                graph.add_dependency(statement, scope[name])

    return graph
