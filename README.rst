===========
pathlib-abc
===========

|pypi| |docs|

Base classes for ``pathlib.Path``-ish objects. Requires Python 3.9+.

This package is a preview of ``pathlib`` functionality planned for a future
release of Python; specifically, it provides three ABCs that can be used to
implement path classes for non-local filesystems, such as archive files and
storage servers:

``JoinablePath``
  Abstract base class for paths that do not perform I/O.
``ReadablePath``
  Abstract base class for paths that support reading.
``WritablePath``
  Abstract base class for paths that support writing.

These base classes are under active development. Once the base classes reach
maturity, they may become part of the Python standard library, and this
package will continue to provide a backport for older Python releases.


Contributing
------------

Functional changes must be made in the upstream CPython project, and undergo
their usual CLA + code review process. Once a change lands in CPython, it can
be back-ported here.

Other changes (such as CI improvements) can be made as pull requests to this
project.



.. |pypi| image:: https://img.shields.io/pypi/v/pathlib-abc.svg
    :target: https://pypi.python.org/pypi/pathlib-abc
    :alt: Latest version released on PyPi

.. |docs| image:: https://readthedocs.org/projects/pathlib-abc/badge
    :target: http://pathlib-abc.readthedocs.io/en/latest
    :alt: Documentation
