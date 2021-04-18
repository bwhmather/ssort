from ssort._dependencies import statement_dependants, statement_dependencies
from ssort._modules import statement_is_assignment, statement_is_import


def _partition(values, predicate):
    passed = []
    failed = []

    for value in values:
        if predicate(value):
            passed.append(value)
        else:
            failed.append(value)
    return passed, failed


def presort(module):
    statements = list(module.statements())
    output = []

    # TODO add dependency between imports and all non-import statements that
    # precede them.
    imports, statements = _partition(
        statements, lambda statement: statement_is_import(module, statement)
    )
    output += imports

    assignments, statements = _partition(
        statements,
        lambda statement: statement_is_assignment(module, statement),
    )
    output += assignments

    # Output all remaining statements with no dependants followed, recursively
    # by all of the statements that they depend on.
    # The goal here is to try to make it so that dependencies will always be
    # sorted close to the statements that depend on them, and in the order that
    # they are used.  We sort them after their dependants so that they get
    # squeezed down.
    free, statements = _partition(
        statements,
        lambda statement: not list(statement_dependants(module, statement)),
    )
    output += free

    output_set = set(output)
    cursor = 0
    while cursor < len(output):
        for dependency in statement_dependencies(module, output[cursor]):
            if dependency in output_set:
                continue

            if any(
                dependant not in output_set
                for dependant in statement_dependants(module, dependency)
            ):
                continue

            output.append(dependency)
            output_set.add(dependency)
        cursor += 1

    # Anything else was probably part of an isolated cycle.  Add it to the end
    # in the same order it came in.
    output += [
        statement for statement in statements if statement not in output_set
    ]

    return output
