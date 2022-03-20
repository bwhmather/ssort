import argparse
import difflib
import sys

from ssort._exceptions import UnknownEncodingError
from ssort._files import find_python_files
from ssort._ssort import ssort
from ssort._utils import detect_encoding


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

    for path in find_python_files(args.files):
        errors = False

        try:
            original_bytes = path.read_bytes()
        except FileNotFoundError:
            sys.stderr.write(f"ERROR: {str(path)!r} does not exist\n")
            unsortable += 1
            continue
        except IsADirectoryError:
            sys.stderr.write(f"ERROR: {str(path)!r} is a directory\n")
            unsortable += 1
            continue
        except PermissionError:
            sys.stderr.write(f"ERROR: {str(path)!r} is not readable\n")
            unsortable += 1
            continue

        # The logic for converting from bytes to text is duplicated in `ssort`
        # and here because we need access to the text to be able to compute a
        # diff at the end.
        try:
            encoding = detect_encoding(original_bytes)
        except UnknownEncodingError as exc:
            sys.stderr.write(
                f"ERROR: unknown encoding, {exc.encoding!r}, in {str(path)!r}\n"
            )
            unsortable += 1
            continue

        try:
            original = original_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            sys.stderr.write(
                f"ERROR: encoding error in {str(path)!r}: {exc}\n"
            )
            unsortable += 1
            continue

        def _on_parse_error(message, *, lineno, col_offset, **kwargs):
            nonlocal errors
            errors = True

            sys.stderr.write(
                f"ERROR: syntax error in {str(path)!r}: "
                + f"line {lineno}, column {col_offset}\n"
            )

        def _on_unresolved(message, *, name, lineno, col_offset, **kwargs):
            nonlocal errors
            errors = True

            sys.stderr.write(
                f"ERROR: unresolved dependency {name!r} "
                + f"in {str(path)!r}: "
                + f"line {lineno}, column {col_offset}\n"
            )

        def _on_wildcard_import(**kwargs):
            sys.stderr.write(
                "WARNING: can't determine dependencies on * import\n"
            )

        try:
            updated = ssort(
                original,
                filename=str(path),
                on_parse_error=_on_parse_error,
                on_unresolved=_on_unresolved,
                on_wildcard_import=_on_wildcard_import,
            )

            if errors:
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
                path.write_text(updated, encoding=encoding)
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
        if not unsorted and not unchanged and not unsortable:
            summary.append("No files are present to be sorted. Nothing to do.")

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
        if not unsorted and not unchanged and not unsortable:
            summary.append("No files are present to be sorted. Nothing to do.")

        sys.stderr.write(", ".join(summary) + "\n")

        if unsortable:
            sys.exit(1)
