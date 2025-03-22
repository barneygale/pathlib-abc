"""
Protocols for supporting classes in pathlib.
"""

# This module also provides abstract base classes for rich path objects.
# These ABCs are a *private* part of the Python standard library, but they're
# made available as a PyPI package called "pathlib-abc". It's possible they'll
# become an official part of the standard library in future.
#
# Three ABCs are provided -- _JoinablePath, _ReadablePath and _WritablePath


from abc import ABC, abstractmethod
from pathlib_abc._glob import _PathGlobber
from pathlib_abc._os import magic_open, ensure_distinct_paths, ensure_different_files, copyfileobj
from typing import Optional, Protocol, runtime_checkable


__all__ = ['PathParser', 'PathInfo', 'JoinablePath', 'ReadablePath', 'WritablePath', 'magic_open']


def _explode_path(path):
    """
    Split the path into a 2-tuple (anchor, parts), where *anchor* is the
    uppermost parent of the path (equivalent to path.parents[-1]), and
    *parts* is a reversed list of parts following the anchor.
    """
    split = path.parser.split
    path = str(path)
    parent, name = split(path)
    names = []
    while path != parent:
        names.append(name)
        path = parent
        parent, name = split(path)
    return path, names


@runtime_checkable
class _PathParser(Protocol):
    """Protocol for path parsers, which do low-level path manipulation.

    Path parsers provide a subset of the os.path API, specifically those
    functions needed to provide JoinablePath functionality. Each JoinablePath
    subclass references its path parser via a 'parser' class attribute.
    """

    sep: str
    altsep: Optional[str]
    def split(self, path: str) -> tuple[str, str]: ...
    def splitext(self, path: str) -> tuple[str, str]: ...
    def normcase(self, path: str) -> str: ...


@runtime_checkable
class PathInfo(Protocol):
    """Protocol for path info objects, which support querying the file type.
    Methods may return cached results.
    """
    def exists(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_dir(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_file(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_symlink(self) -> bool: ...


class _JoinablePath(ABC):
    """Abstract base class for pure path objects.

    This class *does not* provide several magic methods that are defined in
    its implementation PurePath. They are: __init__, __fspath__, __bytes__,
    __reduce__, __hash__, __eq__, __lt__, __le__, __gt__, __ge__.
    """
    __slots__ = ()

    @property
    @abstractmethod
    def parser(self):
        """Implementation of pathlib._types.Parser used for low-level path
        parsing and manipulation.
        """
        raise NotImplementedError

    @abstractmethod
    def with_segments(self, *pathsegments):
        """Construct a new path object from any number of path-like objects.
        Subclasses may override this method to customize how new path objects
        are created from methods like `iterdir()`.
        """
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        """Return the string representation of the path, suitable for
        passing to system calls."""
        raise NotImplementedError

    @property
    def anchor(self):
        """The concatenation of the drive and root, or ''."""
        return _explode_path(self)[0]

    @property
    def name(self):
        """The final path component, if any."""
        return self.parser.split(str(self))[1]

    @property
    def suffix(self):
        """
        The final component's last suffix, if any.

        This includes the leading period. For example: '.txt'
        """
        return self.parser.splitext(self.name)[1]

    @property
    def suffixes(self):
        """
        A list of the final component's suffixes, if any.

        These include the leading periods. For example: ['.tar', '.gz']
        """
        split = self.parser.splitext
        stem, suffix = split(self.name)
        suffixes = []
        while suffix:
            suffixes.append(suffix)
            stem, suffix = split(stem)
        return suffixes[::-1]

    @property
    def stem(self):
        """The final path component, minus its last suffix."""
        return self.parser.splitext(self.name)[0]

    def with_name(self, name):
        """Return a new path with the file name changed."""
        split = self.parser.split
        if split(name)[0]:
            raise ValueError(f"Invalid name {name!r}")
        path = str(self)
        path = path.removesuffix(split(path)[1]) + name
        return self.with_segments(path)

    def with_stem(self, stem):
        """Return a new path with the stem changed."""
        suffix = self.suffix
        if not suffix:
            return self.with_name(stem)
        elif not stem:
            # If the suffix is non-empty, we can't make the stem empty.
            raise ValueError(f"{self!r} has a non-empty suffix")
        else:
            return self.with_name(stem + suffix)

    def with_suffix(self, suffix):
        """Return a new path with the file suffix changed.  If the path
        has no suffix, add given suffix.  If the given suffix is an empty
        string, remove the suffix from the path.
        """
        stem = self.stem
        if not stem:
            # If the stem is empty, we can't make the suffix non-empty.
            raise ValueError(f"{self!r} has an empty name")
        elif suffix and not suffix.startswith('.'):
            raise ValueError(f"Invalid suffix {suffix!r}")
        else:
            return self.with_name(stem + suffix)

    @property
    def parts(self):
        """An object providing sequence-like access to the
        components in the filesystem path."""
        anchor, parts = _explode_path(self)
        if anchor:
            parts.append(anchor)
        return tuple(reversed(parts))

    def joinpath(self, *pathsegments):
        """Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).
        """
        return self.with_segments(str(self), *pathsegments)

    def __truediv__(self, key):
        try:
            return self.with_segments(str(self), key)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, key):
        try:
            return self.with_segments(key, str(self))
        except TypeError:
            return NotImplemented

    @property
    def parent(self):
        """The logical parent of the path."""
        path = str(self)
        parent = self.parser.split(path)[0]
        if path != parent:
            return self.with_segments(parent)
        return self

    @property
    def parents(self):
        """A sequence of this path's logical parents."""
        split = self.parser.split
        path = str(self)
        parent = split(path)[0]
        parents = []
        while path != parent:
            parents.append(self.with_segments(parent))
            path = parent
            parent = split(path)[0]
        return tuple(parents)

    def full_match(self, pattern):
        """
        Return True if this path matches the given glob-style pattern. The
        pattern is matched against the entire path.
        """
        if not hasattr(pattern, 'with_segments'):
            pattern = self.with_segments(pattern)
        case_sensitive = self.parser.normcase('Aa') == 'Aa'
        globber = _PathGlobber(pattern.parser.sep, case_sensitive, recursive=True)
        match = globber.compile(str(pattern), altsep=pattern.parser.altsep)
        return match(str(self)) is not None


class _ReadablePath(_JoinablePath):
    """Abstract base class for readable path objects.

    The Path class implements this ABC for local filesystem paths. Users may
    create subclasses to implement readable virtual filesystem paths, such as
    paths in archive files or on remote storage systems.
    """
    __slots__ = ()

    @property
    @abstractmethod
    def info(self):
        """
        A PathInfo object that exposes the file type and other file attributes
        of this path.
        """
        raise NotImplementedError

    @abstractmethod
    def __open_rb__(self, buffering=-1):
        """
        Open the file pointed to by this path for reading in binary mode and
        return a file object, like open(mode='rb').
        """
        raise NotImplementedError

    def read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        with magic_open(self, mode='rb', buffering=0) as f:
            return f.read()

    def read_text(self, encoding=None, errors=None, newline=None):
        """
        Open the file in text mode, read it, and close the file.
        """
        with magic_open(self, mode='r', encoding=encoding, errors=errors, newline=newline) as f:
            return f.read()

    @abstractmethod
    def iterdir(self):
        """Yield path objects of the directory contents.

        The children are yielded in arbitrary order, and the
        special entries '.' and '..' are not included.
        """
        raise NotImplementedError

    def glob(self, pattern, *, recurse_symlinks=True):
        """Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given relative pattern.
        """
        if not hasattr(pattern, 'with_segments'):
            pattern = self.with_segments(pattern)
        anchor, parts = _explode_path(pattern)
        if anchor:
            raise NotImplementedError("Non-relative patterns are unsupported")
        elif not recurse_symlinks:
            raise NotImplementedError("recurse_symlinks=False is unsupported")
        case_sensitive = self.parser.normcase('Aa') == 'Aa'
        globber = _PathGlobber(self.parser.sep, case_sensitive, recursive=True)
        select = globber.selector(parts)
        return select(self.joinpath(''))

    def walk(self, top_down=True, on_error=None, follow_symlinks=False):
        """Walk the directory tree from this directory, similar to os.walk()."""
        paths = [self]
        while paths:
            path = paths.pop()
            if isinstance(path, tuple):
                yield path
                continue
            dirnames = []
            filenames = []
            if not top_down:
                paths.append((path, dirnames, filenames))
            try:
                for child in path.iterdir():
                    if child.info.is_dir(follow_symlinks=follow_symlinks):
                        if not top_down:
                            paths.append(child)
                        dirnames.append(child.name)
                    else:
                        filenames.append(child.name)
            except OSError as error:
                if on_error is not None:
                    on_error(error)
                if not top_down:
                    while not isinstance(paths.pop(), tuple):
                        pass
                continue
            if top_down:
                yield path, dirnames, filenames
                paths += [path.joinpath(d) for d in reversed(dirnames)]

    @abstractmethod
    def readlink(self):
        """
        Return the path to which the symbolic link points.
        """
        raise NotImplementedError

    def copy(self, target, **kwargs):
        """
        Recursively copy this file or directory tree to the given destination.
        """
        if not hasattr(target, 'with_segments'):
            target = self.with_segments(target)
        ensure_distinct_paths(self, target)
        try:
            copy_to_target = target._copy_from
        except AttributeError:
            raise TypeError(f"Target path is not writable: {target!r}") from None
        copy_to_target(self, **kwargs)
        return target.joinpath()  # Empty join to ensure fresh metadata.

    def copy_into(self, target_dir, **kwargs):
        """
        Copy this file or directory tree into the given existing directory.
        """
        name = self.name
        if not name:
            raise ValueError(f"{self!r} has an empty name")
        elif hasattr(target_dir, 'with_segments'):
            target = target_dir / name
        else:
            target = self.with_segments(target_dir, name)
        return self.copy(target, **kwargs)


class _WritablePath(_JoinablePath):
    """Abstract base class for writable path objects.

    The Path class implements this ABC for local filesystem paths. Users may
    create subclasses to implement writable virtual filesystem paths, such as
    paths in archive files or on remote storage systems.
    """
    __slots__ = ()

    @abstractmethod
    def symlink_to(self, target, target_is_directory=False):
        """
        Make this path a symlink pointing to the target path.
        Note the order of arguments (link, target) is the reverse of os.symlink.
        """
        raise NotImplementedError

    @abstractmethod
    def mkdir(self):
        """
        Create a new directory at this given path.
        """
        raise NotImplementedError

    @abstractmethod
    def __open_wb__(self, buffering=-1):
        """
        Open the file pointed to by this path for writing in binary mode and
        return a file object, like open(mode='wb').
        """
        raise NotImplementedError

    def write_bytes(self, data):
        """
        Open the file in bytes mode, write to it, and close the file.
        """
        # type-check for the buffer interface before truncating the file
        view = memoryview(data)
        with magic_open(self, mode='wb') as f:
            return f.write(view)

    def write_text(self, data, encoding=None, errors=None, newline=None):
        """
        Open the file in text mode, write to it, and close the file.
        """
        if not isinstance(data, str):
            raise TypeError('data must be str, not %s' %
                            data.__class__.__name__)
        with magic_open(self, mode='w', encoding=encoding, errors=errors, newline=newline) as f:
            return f.write(data)

    def _copy_from(self, source, follow_symlinks=True):
        """
        Recursively copy the given path to this path.
        """
        stack = [(source, self)]
        while stack:
            src, dst = stack.pop()
            if not follow_symlinks and src.info.is_symlink():
                dst.symlink_to(str(src.readlink()), src.info.is_dir())
            elif src.info.is_dir():
                children = src.iterdir()
                dst.mkdir()
                for child in children:
                    stack.append((child, dst.joinpath(child.name)))
            else:
                ensure_different_files(src, dst)
                with magic_open(src, 'rb') as source_f:
                    with magic_open(dst, 'wb') as target_f:
                        copyfileobj(source_f, target_f)


PathParser = _PathParser
JoinablePath = _JoinablePath
ReadablePath = _ReadablePath
WritablePath = _WritablePath
