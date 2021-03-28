import builtins

from ssort._bindings import get_bindings
from ssort._dependencies import get_dependencies
from ssort._parsing import split
from ssort._sorting import sort


def ssort(text, *, filename="<unknown>"):
    statement_nodes = []
    statement_texts = []
    statement_dependencies = []

    # A dictionary mapping from names to statement indexes.
    scope = {}

    for text, node in split(text, filename=filename):
        statement_id = len(statement_nodes)

        dependencies = []
        for dependency in get_dependencies(node):
            dependencies.append(scope.get(dependency.name, dependency.name))

        for name in get_bindings(node):
            scope[name] = statement_id

        statement_texts.append(text)
        statement_nodes.append(node)
        statement_dependencies.append(dependencies)

    # Patch up dependencies that couldn't be resolved immediately.
    statement_dependencies = [
        [
            dependency
            if isinstance(dependency, int)
            else scope.get(dependency, dependency)
            for dependency in dependencies
        ]
        for dependencies in statement_dependencies
    ]

    statement_dependencies = [
        [
            dependency
            for dependency in dependencies
            if not isinstance(dependency, str)
            or dependency not in builtins.__dict__
        ]
        for dependencies in statement_dependencies
    ]

    for dependencies in statement_dependencies:
        for dependency in dependencies:
            if isinstance(dependency, str):
                raise Exception(f"Could not resolve dependency {dependency!r}")

    sorted_statements = sort(statement_dependencies)

    print(
        "\n".join(
            statement_texts[statement] for statement in sorted_statements
        )
    )
