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

    $ ssort src/ tests/; isort src/ tests/; black src/ tests/

You can also setup ssort to run automatically before commit by setting up `pre-commit <https://pre-commit.com/index.html>`_,
and registering ssort in your `.pre-commit-config.yaml`.

.. code:: yaml

  repos:
  # ...
  - repo: https://github.com/bwhmather/ssort
    rev: master
    hooks:
    - id: ssort
  - repo: https://github.com/pycqa/isort
    rev: master
    hooks:
    - id: isort
      name: isort (python)
      args: [--profile=black]
  - repo: https://github.com/psf/black
    rev: master
    hooks:
    - id: black

.. end-usage


Output
======
.. begin-output

``ssort`` will sort top level statements and statements in class bodies.

When sorting top level statements, ``ssort`` follows three simple rules:

- Statements must always be moved after the statements that they depend on, unless there is a cycle.
- If there is a cycle, the order of statements within the cycle must not be changed.
- If there is no dependency between statements then, to the greatest extent possible, the original order should be kept.

These rules result in low level building blocks being moved to the top of modules, with higher level logic going at the bottom.
The `FAQ <#why-does-ssort-sort-bottom-up-rather-than-top-down>`_ goes into some detail about why this order was chosen.

The rules for sorting class bodies are more complicated.
Class methods are generally only called from outside the class and so there aren't usually many interdependencies from which to derive structure.
``ssort`` therefore ignores (deferred) dependencies between d`under and public methods and instead divides up class statements into hard-coded groups that it arranges in the following order:

- The class docstring.
- Special attributes, i.e. ``__slots__`` or ``__doc__``.
- Inner classes.
- Regular attributes.
- Lifecycle d'under methods, e.g. ``__init__`` or ``__new__``.
- Public methods, and unused private methods.
- Other d'under methods, e.g. ``__getattr__`` or ``__len__``.

Apart from the docstring, this order is essentially arbitrary.
It is was chosen as being representative of current standard industry practice.

D'under methods are arranged in a hard coded order within their group.
Statements in other groups are left in their original order.

Private methods should only be called from other methods in the class, and so are mixed in topologically.

If a class-definition-time dependency is detected between two statements preserving the relative order of the linked statements will take priority.

.. end-output


Frequently Asked Questions
==========================
.. begin-faq

Why does ``ssort`` sort bottom-up rather than top-down?
-------------------------------------------------------

Python is a scripting language, which means that the body of each module is evaluated, statement by statement, from top to bottom.
In almost all cases, things must be defined before they can be used.
Attempting, in the subset of cases where it is possible, to reverse the order is difficult to do safely and leads to inconsistency with the cases where top-down ordering is impossible.


Top-down ordering is only possible when lookups are deferred
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Top-down ordering is only possible when lookups are deferred, but in most cases, lookups happen immediately.

.. code:: python

    # Broken.

    variable = dependency()

    def dependency():
        ...

In this example python will try to find ``dependency`` in the ``locals()`` dict when the first line is evaluated, and fail because the statement that defines it has not been evaluated yet.

As far as I am aware, there is only one way to reference a variable that has not been bound yet, and that is to close over it in a function definition.

.. code:: python

    # Working.

    def function():
        return dependency()

    def dependency():
        ...

This is because the lookup is deferred until after ``function`` is called, which in this case doesn't happen until both functions are defined.


Top-down ordering fails unsafe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

A naive analysis would suggest that ``_shared_dep`` is a runtime dependency and can safely be moved to the bottom of the script.

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

This will result in a ``NameError`` as ``_shared_dep`` will not have been bound when ``_decorator`` is invoked.

More powerful static analysls can mitigate this problem, but any missed hard references are likely to result in the program being broken.
Bottom-up sorting can only force broken reorderings when static analysis misses a reference that results in a cycle.


Top-down ordering needs special cases for constants and imports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even the most die hard proponent of top down ordering would not argue that ``import`` statements should be moved to the bottom of the file.

Take the following example:

.. code:: python

    from module import first_dep

    def second_dep():
        ...

    @decorator
    def function():
        first_dep()
        second_dep()

A strict top-down sort would see it reordered with the ``first_dep`` import at the bottom of the file.

.. code:: python

    from other_module import decorator

    @decorator
    def function():
        first_dep()
        second_dep()

    def second_dep():
        ...

    from module import first_dep


Top-down ordering makes code navigation difficult
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
With bottom-up ordering, navigation is easy.
If you want to find where a variable is defined you scroll up.
If you want to find where a variable is used you scroll down.
These rules are reliable, and straightforward for programmers to learn and apply.

With top-down order, navigation is more tricky.
If you want to find where a variable is defined you scroll down, unless the variable is a constant or an import, or the variable is referenced here at import time, or the variable is referenced somewhere else at import time, or any of the many other special cases.
If you want to find where a variable is used, you basically have to scan the whole file.

Every special case added to the sorting tool is a special case that programmers need to learn if they are to navigate quickly, and top-down ordering requires a lot of special cases.


Why doesn't ssort allow me to configure X?
------------------------------------------

``ssort`` aims to bring about ecosystem wide consistency in how python source files are organised.
If this can be achieved then it will help all programmers familiar with its conventions to navigate unfamiliar codebases, and it will reduce arguments between programmers who prefer different conventions.
This only works if those conventions can't be changed.


Why was ssort created?
----------------------

``ssort`` exists because its author was too lazy to implement jump-to-definition in his text editor, and decided that it would be easier to just reformat all of the world's python code to make it possible to navigate by scrolling.

.. end-faq


Links
=====

- Source code: https://github.com/bwhmather/ssort
- Issue tracker: https://github.com/bwhmather/ssort/issues
- PyPI: https://pypi.python.org/pypi/ssort


License
=======

The project is made available under the terms of the MIT license.  See `LICENSE <./LICENSE>`_ for details.

.. end-docs
