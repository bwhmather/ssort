import ast
import dataclasses
from typing import List

from ssort._bindings import get_bindings
from ssort._dependencies import get_dependencies


@dataclasses.dataclass(frozen=True)
class _Statement:
    start_lineno: int
    start_col_offset: int
    end_lineno: int
    end_col_offset: int

    assigned_names: List[str]
    dependencies: List[str]


def ssort(f):
    root = ast.parse(f.read(), "example.py")
    print(ast.dump(root, include_attributes=True, indent=2))

    statements = []
    # A dictionary mapping from names to statement indexes.
    scope = {}

    cursor_lineno = 0
    cursor_col_offset = 0

    for node in root.body:
        start_lineno = cursor_lineno
        start_col_offset = cursor_col_offset
        end_lineno = node.end_lineno
        end_col_offset = node.end_col_offset

        cursor_lineno = end_lineno
        cursor_col_offset = end_col_offset

        statement_id = len(statements)

        dependencies = []
        for dependency in get_dependencies(node):
            dependencies.append(scope.get(dependency, dependency))

        # statement.dependencies = dependencies
        # statements.append(statement)

        print(get_dependencies(node))
        print(get_bindings(node))
        for name in get_bindings(node):
            scope[name] = statement_id

    # Patch up dependencies that couldn't be resolved immediately.
    for statement in statements:
        for dependency in dependencies:
            if isinstance(dependency, str):
                dependency = scope[dependency]
