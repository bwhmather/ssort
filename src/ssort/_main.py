import argparse
import difflib
import pathlib
import sys

from ssort._dependencies import ResolutionError
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

    unsorted = 0
    unsortable = 0
    unchanged = 0

    paths = _find_files(args.files)
    for path in paths:
        original = path.read_text()

        try:
            updated = ssort(original, filename=str(path))

        except ResolutionError as e:
            for req in e.unresolved:
                sys.stderr.write(
                    f"ERROR: unresolved dependency {req.name!r} "
                    + f"in {str(path)!r}: "
                    + f"line {req.lineno}, column {req.col_offset}\n"
                )
            unsortable += 1
            continue

        except SyntaxError as e:
            sys.stderr.write(
                f"ERROR: syntax error in {str(path)!r}: "
                + f"line {e.lineno}, column {e.offset}\n"
            )
            unsortable += 1
            continue

        except Exception as e:
            raise Exception(f"ERROR while sorting {path}\n") from e

        if original != updated:
            unsorted += 1
            if args.check:
                sys.stderr.write(
                    f"ERROR: {str(path)!r} is incorrectly sorted\n"
                )
            else:
                sys.stderr.write(f"Sorting {str(path)!r}\n")
                path.write_text(updated)
        else:
            unchanged += 1

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

        def _fmt_count(count):
            return f"{count} file" if count == 1 else f"{count} files"

        summary = []
        if unsorted:
            summary.append(f"{_fmt_count(unsorted)} would be resorted")
        if unchanged:
            summary.append(f"{_fmt_count(unchanged)} would be left unchanged")
        if unsortable:
            summary.append(f"{_fmt_count(unsortable)} would not be sortable")

        sys.stderr.write(", ".join(summary) + "\n")

        if unsorted or unsortable:
            sys.exit(1)

    else:

        def _fmt_count_were(count):
            if count == 1:
                return f"{count} file was"
            else:
                return f"{count} files were"

        summary = []
        if unsorted:
            summary.append(f"{_fmt_count_were(unsorted)} resorted")
        if unchanged:
            summary.append(f"{_fmt_count_were(unchanged)} left unchanged")
        if unsortable:
            summary.append(f"{_fmt_count_were(unsortable)} not sortable")

        sys.stderr.write(", ".join(summary) + "\n")

        if unsortable:
            sys.exit(1)
