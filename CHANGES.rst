Version History
===============

Unreleased
----------

- Nothing yet


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
