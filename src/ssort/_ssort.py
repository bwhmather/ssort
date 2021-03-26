from ssort._bindings import get_bindings
from ssort._dependencies import get_dependencies
from ssort._parsing import split
from ssort._sorting import sort


def ssort(f):
    statement_nodes = []
    statement_texts = []
    statement_dependencies = []

    # A dictionary mapping from names to statement indexes.
    scope = {}

    for text, node in split(f, "example.py"):
        statement_id = len(statement_nodes)

        dependencies = []
        for dependency_name in get_dependencies(node):
            dependencies.append(scope.get(dependency_name, dependency_name))

        for name in get_bindings(node):
            scope[name] = statement_id

        statement_texts.append(text)
        statement_nodes.append(node)
        statement_dependencies.append(dependencies)

    # Patch up dependencies that couldn't be resolved immediately.
    for dependencies in statement_dependencies:
        for index, dependency in enumerate(dependencies):
            if isinstance(dependency, str):
                dependencies[index] = scope[dependency]

    sorted_statements = sort(statement_dependencies)

    print(
        "\n".join(
            statement_texts[statement] for statement in sorted_statements
        )
    )
