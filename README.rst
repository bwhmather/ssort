*****
SSort
*****

|build-status| |coverage|

.. |build-status| image:: https://github.com/bwhmather/ssort/actions/workflows/ci.yaml/badge.svg?branch=master
    :target: https://github.com/bwhmather/ssort/actions/workflows/ci.yaml
    :alt: Build Status

.. |coverage| image:: https://coveralls.io/repos/github/bwhmather/ssort/badge.svg?branch=master
    :target: https://coveralls.io/github/bwhmather/ssort?branch=master
    :alt: Cocerage


.. begin-docs

The python source code sorter.

Sorts the contents of python modules so that statements are placed after the things they depend on, but leaves grouping to the programmer.
Groups class members by type and enforces topological sorting of methods.

Makes old fashioned code navigation easier, you can always scroll up to see where something is defined, and reduces bikeshedding.

Compatible with and intended to complement `isort <https://pycqa.github.io/isort/>`_ and `black <https://black.readthedocs.io/en/stable/>`_.


Before:

.. code:: python

    from module import BaseClass

    def function():
        return _dependency()

    def _decorator(fn):
        return fn

    @_decorator
    def _dependency():
        return Class()

    class Class(BaseClass):
        def public_method(self):
            return self

        def __init__(self):
            pass

After:

.. code:: python

    from module import BaseClass

    class Class(BaseClass):
        def __init__(self):
            pass

        def public_method(self):
            return self

    def _decorator(fn):
        return fn

    @_decorator
    def _dependency():
        return Class()

    def function():
        return _dependency()


Installation
============
.. begin-installation

SSort can be installed manually using pip.

.. code:: bash

    $ pip install ssort

.. end-installation


Usage
=====
.. begin-usage

To check that a file is correctly sorted use the `--check` flag.
`--diff` can be passed to see what changes ``ssort`` would make.

.. code:: bash

    $ ssort --check --diff path/to/python_module.py


To allow ``ssort`` to rearrange your file, simply invoke with no extra flags.
If ``ssort`` needs to make changes to a `black <https://black.readthedocs.io/en/stable/>`_ conformant file, the result will not necessarily be `black <https://black.readthedocs.io/en/stable/>`_ conformant.
The result of running `black <https://black.readthedocs.io/en/stable/>`_ on an ``ssort`` conformant file will always be ``ssort`` conformant.
We recommend that you reformat using `isort <https://pycqa.github.io/isort/>`_ and `black <https://black.readthedocs.io/en/stable/>`_ immediately after running ``ssort``.

.. code:: bash

    $ ssort src/ tests/ setup.py; isort src/ tests/ setup.py; black src/ tests/ setup.py

You can also setup ssort to run automatically before commit by setting up `pre-commit <https://pre-commit.com/index.html>`_,
and registering ssort in your `.pre-commit-config.yaml`.

.. code:: yaml

  repos:
  # ...
  - repo: https://github.com/bwhmather/ssort
    rev: 0.11.5
    hooks:
    - id: ssort
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
    - id: isort
      name: isort (python)
      args: [--profile=black]
  - repo: https://github.com/psf/black
    rev: 22.1.0
    hooks:
    - id: black

.. end-usage


Output
======
.. begin-output

`ssort` will sort top level statements and statements in classes.

When sorting top level statements, `ssort` follows three simple rules:
  - Statements must always be moved after the statements that they depend on, unless there is a cycle.
  - If there is a cycle, the order of statements within the cycle must not be changed.
  - If there is no dependency between statements then, to the greatest extent possible, the original order should be kept.


`ssort` is more opinionated about the order of statements in classes:
  - Class attributes should be moved to the top of the class and must always be kept in their original order.
  - Lifecycle (`__init__`, `__new__`, etc) methods, and the methods they depend on, should go next.
  - Regular methods follow, dependencies always ahead of the methods that depend on them.
  - Other d'under methods should go at the end in a fixed order.

.. end-output


Frequently Asked Questions
==========================
.. begin-output

Why does ``ssort`` sort bottom-up rather than top-down?
-------------------------------------------------------

In short, python is a scripting language, which means that the body of each module is evaluated, statement by statement, from top to bottom.  In almost all cases, things must be defined before they can be used.

Many people, particularly those with a background in non-scripting languages


Top-down ordering is only possible when lookups are deferred
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Top-down ordering is only possible when lookups are deferred, but in most cases, lookups happen immediately.

.. code:: python

    # Broken.

    variable = dependency()

    def dependency():
        ...

In this example python will try to find ``dependency`` in the ``locals()`` dict when the first line is evaluated, and fail because the statement that defines it has not been evaluated yet.

In a limited set of cases, basically only when a function definition closes over a variable in module scope, it's possible for you to reference a variable that hasn't been bound yet.

.. code:: python

    # Working.

    def function():
        return dependency()

    def dependency():
        ...

This is because the lookup is deferred until after ``function`` is called, which in this case doesn't happen until both functions are defined.


Unsafe to do even when a function closes over a variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In cases where lookups are deferred, they may not be deferred sufficiently far to allow the dependant statement to be sorted before its dependencies.

Take the following example formatted in bottom-up order.

.. code:: python

    # Hidden runtime dependency example sorted bottom-up.

    def _shared_dep():
        ...

    def _decorator(fn):
        _shared_dep()
        return fn

    @_decorator
    def top_level():
        _shared_dep()

A naive analysis would suggest that `_shared_dep` is a runtime dependency and can safely be moved to the bottom of the script.

.. code:: python

    # Hidden runtime dependency example sorted top-down using naive analysis.

    def _decorator(fn):
        _shared_dep()
        return fn

    @_decorator
    def top_level():
        _shared_dep()

    def _shared_dep():
        ...

Unfortunately, this will result in a ``NameError`` as `_shared_dep` will not have been bound when `_decorator` is invoked.


Needs to be overridden for constants and imports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from module import first_dep

    def second_dep():
        ...

    def function():
        first_dep()
        second_dep()


.. code:: python

    def function():
        first_dep()
        second_dep()

    def second_dep():
        ...

    from module import first_dep


Workarounds exist.
Read module from bottom to top.



It undermines the reason for having `ssort`.
`ssort` exists primarily because the author was fed up with inconsistently applied top-down sorting making it impossible to know which way to scroll to get to the definition of a variable.

With top-down:
  - Scroll down to look for definition in module.
  - Scroll up to look for imports and special cases.

With bottom-up:
  - Scroll up


Ecosystem-wide consistency is valuable.





















In short, because top-down requires too many special cases and, even if those special

In short, because there it is impossible to consistently define things after that are referenced.


Python is a scripting language so modules are actually evaluated from top to bottom.
Putting high level logic up top is nice when you just have functions, which defer lookup until they are called, but you quickly run into places (decorators, base classes) where it doesn't work and then you have to switch. Better to use the same convention everywhere. You quickly get used to reading a module from bottom to top.


With enough special cases, and with deep enough static analysis, all of this might be overcome, but the we hit the final obstable which is that expecting our users to internalize this logic and build a mental model that matches it is untenable.


.. end-output


Links
=====

- Source code: https://github.com/bwhmather/ssort
- Issue tracker: https://github.com/bwhmather/ssort/issues
- PyPI: https://pypi.python.org/pypi/ssort


License
=======

The project is made available under the terms of the MIT license.  See `LICENSE <./LICENSE>`_ for details.

.. end-docs
