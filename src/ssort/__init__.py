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
import argparse
import difflib
import pathlib
import sys

from ssort._ssort import ssort

__version__ = "0.1.0"


def _find_files(patterns):
    if not patterns:
        patterns = ["."]

    paths = set()
    for pattern in patterns:
        path = pathlib.Path(pattern)
        if path.suffix == ".py":
            paths.add(path)
        else:
            paths.update(path.glob("**/*.py"))

    return list(paths)


def _main():
    parser = argparse.ArgumentParser(
        description="Sort python statements into dependency order",
    )

    parser.add_argument(
        "--diff",
        dest="show_diff",
        action="store_true",
        help="Prints a diff of all changes ssort would make to a file.",
    )
    parser.add_argument(
        "--check",
        dest="check",
        action="store_true",
        help="Check the file for unsorted statements.  Returns 0 if nothing "
        "needs to be changed.  Otherwise returns 1.",
    )
    parser.add_argument(
        "files", nargs="*", help="One or more python files to sort"
    )

    args = parser.parse_args()

    errors = False
    for path in _find_files(args.files):
        original = path.read_text()

        try:
            updated = ssort(original, filename=str(path))
        except Exception as e:
            raise Exception(f"ERROR while sorting {path}\n") from e

        if args.check:
            if original != updated:
                sys.stderr.write(f"ERROR: {path} is incorrectly sorted.\n")
                errors = True
        else:
            path.write_text(updated)

        if args.show_diff:
            sys.stderr.writelines(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    updated.splitlines(keepends=True),
                    fromfile=f"{path}:before",
                    tofile=f"{path}:after",
                )
            )

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    _main()
