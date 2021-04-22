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

Compatible with and intended to complement `isort <https://pycqa.github.io/isort/>`_ and `black <https://black.readthedocs.io/en/stable/`_.


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

.. code:: bash

    $ ssort path/to/python_module.py


.. end-usage


Links
-----

- Source code: https://github.com/bwhmather/ssort
- Issue tracker: https://github.com/bwhmather/ssort/issues
- PyPI: https://pypi.python.org/pypi/ssort


License
-------

The project is made available under the terms of the MIT license.  See `LICENSE <./LICENSE>`_ for details.

.. end-docs
