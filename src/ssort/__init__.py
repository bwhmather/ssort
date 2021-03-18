"""
Steps:
  - Identify chunks of file representing classes, declarations and functions.
  - Parse each chunk to identify dependencies.
  - Apply a stable topological sort.




Identifying chunks:
  - Comments should be attached to whatever comes after them.



Weird things to handle:
  - Unpacking resulting in multiple assignments.
  - Semicolons resulting in multiple statements on same line.
  - Comments attached to assignments.
  - Redefinitions.
  - Cycles.
  - Immediate dependencies (e.g. decorators) vs deferred dependencies (e.g.
    closed over variables)
  - Deferred dependencies being re-evaluated part way through the file.
  - Preventing re-ordering.
  - Type annotations.

Handling the difference between immediate and deferred deps:
  - Treat all dependencies the same.
  - Try to resolve dependencies immediately.
  - If that fails, resolve dependencies at the very end.


Extensions:
  - Class members.
  - Closures.

"""


import ast
import dataclasses
import functools
from typing import List

__version__ = "0.1.0"


@dataclasses.dataclass(frozen=True)
class _Statement:
    start_lineno: int
    start_col_offset: int
    end_lineno: int
    end_col_offset: int

    assigned_names: List[str]
    dependencies: List[str]


@functools.singledispatch
def _assigned_names(node):
    return []


@_assigned_names.register(ast.FunctionDef)
def _assigned_names_for_function_def(node):
    return [node.name]


@_assigned_names.register(ast.ClassDef)
def _assigned_names_for_class_def(node):
    return [node.name]


@_assigned_names.register(ast.Assign)
def _assigned_names_for_assign(node):
    return [target.id for target in node.targets]


@_assigned_names.register(ast.Import)
def _assigned_names_for_import(node):
    return [name.asname if name.asname else name.name for name in node.names]


@functools.singledispatch
def _dependencies(node):
    return []


@_dependencies.register(ast.Name)
def _dependencies_for_name(node):
    return [node.id]


@_dependencies.register(ast.Assign)
def _dependencies_for_assign(node):
    return _dependencies(node.value)


@_dependencies.register(ast.FunctionDef)
def _dependencies_for_function_def(node):
    dependencies = []
    for decorator in node.decorator_list:
        dependencies += _dependencies(decorator)

    scope = set()
    scope.update(arg.arg for arg in node.args.args)  # Guh.
    if node.args.vararg:
        scope.update(node.args.vararg.arg)
    scope.update(arg.arg for arg in node.args.kwonlyargs)
    if node.args.kwarg:
        scope.update(node.args.kwarg.arg)

    for statement in node.body:
        scope.update(_assigned_names(statement))
        dependencies += _dependencies(statement)

    return [dependency for dependency in dependencies if dependency not in scope]


@_dependencies.register(ast.Call)
def _dependencies_for_call(node):
    dependencies = _dependencies(node.func)

    for arg in node.args:
        dependencies += _dependencies(arg)

    for kwarg in node.keywords:
        dependencies += _dependencies(kwarg.value)

    return dependencies


def process(root):
    statements = []
    # A dictionary mapping from names to statement indexes.
    scope = {}

    cursor_lineno = 0
    cursor_col_offset = 0

    for node in root.body:
        start_lineno = cursor_lineno
        start_lineno = cursor_col_offset
        end_lineno = node.end_lineno
        end_col_offset = node.end_col_offset

        cursor_lineno = end_lineno
        cursor_col_offset = end_col_offset

        statement_id = len(statements)

        dependencies = []
        for dependency in _dependencies(node):
            dependencies.append(scope.get(dependency, dependency))

        # statement.dependencies = dependencies
        # statements.append(statement)

        print(_dependencies(node))
        print(_assigned_names(node))
        for name in _assigned_names(node):
            scope[name] = statement_id

    # Patch up dependencies that couldn't be resolved immediately.
    for statement in statements:
        for dependency in dependencies:
            if isinstance(dependency, str):
                dependency = scope[dependency]


def _main():
    with open("example.py", "r") as f:
        root = ast.parse(f.read(), "example.py")

    print(ast.dump(root, include_attributes=True, indent=2))

    process(root)


if __name__ == "__main__":
    _main()
