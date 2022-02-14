SSort
=====

|build-status|

.. |build-status| image:: https://github.com/bwhmather/ssort/actions/workflows/ci.yaml/badge.svg?branch=master
    :target: https://github.com/bwhmather/ssort/actions/workflows/ci.yaml
    :alt: Build Status

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
------------
.. begin-installation

SSort can be installed manually using pip.

.. code:: bash

    $ pip install ssort

.. end-installation


Usage
-----
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
    rev: 0.10.0
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
------
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


Links
-----

- Source code: https://github.com/bwhmather/ssort
- Issue tracker: https://github.com/bwhmather/ssort/issues
- PyPI: https://pypi.python.org/pypi/ssort


License
-------

The project is made available under the terms of the MIT license.  See `LICENSE <./LICENSE>`_ for details.

.. end-docs
