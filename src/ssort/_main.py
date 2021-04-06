import argparse
import difflib
import pathlib
import sys

from ssort._ssort import ssort


def _find_files(patterns):
    if not patterns:
        patterns = ["."]

    paths_set = set()
    paths_list = []
    for pattern in patterns:
        path = pathlib.Path(pattern)
        if path.suffix == ".py":
            subpaths = [path]
        else:
            subpaths = list(path.glob("**/*.py"))

        for subpath in sorted(subpaths):
            if subpath not in paths_set:
                paths_set.add(subpath)
                paths_list.append(subpath)

    return paths_list


def main():
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
    paths = _find_files(args.files)
    for path in paths:
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

    if args.check:
        if errors:
            sys.exit(1)
        else:
            sys.stderr.write(f"{len(paths)} files would be left unchanged")
