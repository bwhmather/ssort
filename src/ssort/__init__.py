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
from ssort._ssort import ssort

__version__ = "0.1.0"


def _main():
    with open("example.py", "r") as f:
        ssort(f.read(), filename="example.py")


if __name__ == "__main__":
    _main()
