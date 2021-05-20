import sys

from ssort._builtins import MODULE_BUILTINS
from ssort._graphs import Graph
from ssort._statements import (
    statement_bindings,
    statement_method_requirements,
    statement_requirements,
)


class ResolutionError(Exception):
    def __init__(self, msg, *, unresolved):
        super().__init__(msg)
        self.unresolved = unresolved


def statements_graph(statements):
    """
    Returns a dictionary mapping from statements to lists of other statements.
    """
    # A dictionary mapping from names to the statements which bind them.
    scope = {}

    all_requirements = []
    resolved = {}

    for statement in statements:
        for requirement in statement_requirements(statement):
            all_requirements.append(requirement)

            # TODO error if requirement is not deferred.
            if requirement.name in scope:
                resolved[requirement] = scope[requirement.name]
                continue

            if requirement.name in MODULE_BUILTINS:
                resolved[requirement] = None
                continue

        for name in statement_bindings(statement):
            scope[name] = statement

    # Patch up dependencies that couldn't be resolved immediately.
    for requirement in all_requirements:
        if requirement in resolved:
            continue

        if requirement.name not in scope:
            continue

        resolved[requirement] = scope[requirement.name]

    if "*" in scope:
        sys.stderr.write("WARNING: can't determine dependencies on * import\n")

        for requirement in all_requirements:
            if requirement in resolved:
                continue

            resolved[requirement] = scope["*"]

    else:
        unresolved = [
            requirement
            for requirement in all_requirements
            if requirement not in resolved
        ]

        if unresolved:
            raise ResolutionError(
                "Could not resolve all requirements", unresolved=unresolved
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
