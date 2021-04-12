import builtins
import sys

from ssort._bindings import get_bindings
from ssort._parsing import split
from ssort._requirements import Requirement, get_requirements
from ssort._sorting import sort

DEFAULT_SCOPE = {
    *builtins.__dict__,
    "__file__",
    "unicode",
    "long",
    "xrange",
    "buffer",
    "bytearray",
    "basestring",
    "WindowsError",
}


def ssort(text, *, filename="<unknown>"):
    statement_nodes = []
    statement_texts = []
    statement_dependencies = []

    # A dictionary mapping from names to statement indexes.
    scope = {}

    for text, node in split(text, filename=filename):
        statement_id = len(statement_nodes)

        dependencies = []
        for requirement in get_requirements(node):
            dependencies.append(scope.get(requirement.name, requirement))

        for name in get_bindings(node):
            scope[name] = statement_id

        statement_texts.append(text)
        statement_nodes.append(node)
        statement_dependencies.append(dependencies)

    # Patch up dependencies that couldn't be resolved immediately.
    statement_dependencies = [
        [
            dependency
            if not isinstance(dependency, Requirement)
            else scope.get(dependency.name, dependency)
            for dependency in dependencies
        ]
        for dependencies in statement_dependencies
    ]

    statement_dependencies = [
        [
            dependency
            for dependency in dependencies
            if not isinstance(dependency, Requirement)
            or dependency.name not in DEFAULT_SCOPE
        ]
        for dependencies in statement_dependencies
    ]

    if "*" in scope:
        sys.stderr.write("WARNING: can't determine dependencies on * import")
        statement_dependencies = [
            [
                dependency
                for dependency in dependencies
                if not isinstance(dependency, Requirement)
            ]
            for dependencies in statement_dependencies
        ]

    else:
        for dependencies in statement_dependencies:
            for dependency in dependencies:
                if isinstance(dependency, Requirement):
                    raise Exception(
                        f"Could not resolve dependency {dependency!r}"
                    )

    sorted_statements = sort(statement_dependencies)

    return (
        "\n".join(
            statement_texts[statement] for statement in sorted_statements
        )
        + "\n"
    )
