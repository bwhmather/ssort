import builtins
import sys

from ssort._modules import statement_bindings, statement_requirements
from ssort._utils import memoize_weak

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


def _dedup(values):
    output = []
    visited = set()
    for value in values:
        if value not in visited:
            output.append(value)
        visited.add(value)
    return output


@memoize_weak
def _statement_graph(module):
    """
    Returns a dictionary mapping from statements to lists of other statements.
    """
    # A dictionary mapping from names to the statements which bind them.
    scope = {}

    # A dictionary mapping from statements to lists of unresolved Requirements.
    unresolved = {}

    dependencies = {}
    dependants = {}

    for statement in module.statements():
        dependencies[statement] = []
        dependants[statement] = []
        unresolved[statement] = []

        for requirement in statement_requirements(module, statement):
            # TODO error if requirement is not deferred.
            if requirement.name in scope:
                dependencies[statement].append(scope[requirement.name])
                continue

            if requirement.name in DEFAULT_SCOPE:
                continue

            unresolved[statement].append(requirement)

        for name in statement_bindings(module, statement):
            scope[name] = statement

    # Patch up dependencies that couldn't be resolved immediately.
    for statement in module.statements():
        remaining = []
        for requirement in unresolved[statement]:
            if requirement.name in scope:
                dependencies[statement].append(scope[requirement.name])
            else:
                remaining.append(requirement.name)
        unresolved[statement] = remaining

    if "*" in scope:
        sys.stderr.write("WARNING: can't determine dependencies on * import")

        for statement in module.statements():
            for requirement in unresolved[statement]:
                dependencies[statement].append(scope["*"])

    else:
        for statement in module.statements():
            for requirement in unresolved[statement]:
                raise Exception(
                    f"Could not resolve requirement {requirement!r}"
                )

    for statement in module.statements():
        for dependency in dependencies[statement]:
            dependants[dependency].append(statement)

    for statement in module.statements():
        dependencies[statement] = _dedup(dependencies[statement])
        dependants[statement] = _dedup(dependants[statement])

    return dependencies, dependants


def statement_dependencies(module, statement):
    dependencies, dependants = _statement_graph(module)
    yield from dependencies[statement]


def statement_dependants(module, statement):
    dependencies, dependants = _statement_graph(module)
    yield from dependants[statement]
