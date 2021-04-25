SSort
=====

|build-status|

.. |build-status| image:: https://github.com/bwhmather/ssort/actions/workflows/ci.yaml/badge.svg?branch=master
    :target: https://github.com/bwhmather/ssort/actions/workflows/ci.yaml
    :alt: Build Status

.. begin-docs

The python statement sorter.

Enforces topological sorting of top level python statements.
Groups class members by types and enforces topological sorting of methods.

Compatible with and intended to complement `isort <https://pycqa.github.io/isort/>`_ and `black <https://black.readthedocs.io/en/stable/>`_.


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
We recommend that you reformat using `isort <https://pycqa.github.io/isort/>`_ and `black <https://black.readthedocs.io/en/stable/>`_ immediately _after_ running ``ssort``.

.. code:: bash

    $ ssort src/ tests/ setup.py; isort src/ tests/ setup.py; black src/ tests/ setup.py

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
