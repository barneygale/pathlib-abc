Version History
===============

Unreleased
----------

- Nothing yet

v0.3.1
------

- Add support for Python 3.7.

v0.3.0
------

- Rename ``PathModuleBase`` to ``ParserBase``, and ``PurePathBase.pathmod``
  to ``PurePathBase.parser``.
- Add ``ParserBase.splitext()``.
- Add ``PurePathBase.full_match()``.
- Treat a single dot ("``.``") as a valid file extension.
- Revert ``match()`` back to 3.12 behaviour (no recursive wildcards).
- Replace ``PathBase.glob(follow_symlinks=...)`` with ``recurse_symlinks=...``.
- Suppress all ``OSError`` exceptions from ``PathBase.exists()`` and
  ``is_*()`` methods.
- Disallow passing ``bytes`` to initialisers.
- Improve walking and globbing performance.
- Expand test coverage.
- Clarify that we're using the PSF license.


v0.2.0
------

- Add ``PathModuleBase`` ABC to support path syntax customization.
- Add CI. Thank you Edgar Ramírez Mondragón!
- Return paths with trailing slashes if a glob pattern ends with a slash.
- Return both files and directory paths if a glob pattern ends with ``**``,
  rather than directories only.
- Improve ``PathBase.resolve()`` performance by avoiding some path object
  allocations.
- Remove ``PurePathBase.is_reserved()``.
- Remove automatic path normalization. Specifically, the ABCs no longer
  convert alternate separators nor remove either dot or empty segments.
- Remove caching of the path drive, root, tail, and string.
- Remove deprecation warnings and audit events.


v0.1.1
------

- Improve globbing performance by avoiding re-initialising path objects.
- Add docs.


v0.1.0
------

- Initial release.
