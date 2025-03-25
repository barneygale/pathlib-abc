API Reference
=============


Functions
---------

This package offers the following functions:

.. function:: magic_open(path, mode='r' buffering=-1, \
                         encoding=None, errors=None, newline=None)

    Open the path and return a file object. Unlike the built-in ``open()``
    function, this function tries to call :meth:`!__open_r__`,
    :meth:`~ReadablePath.__open_rb__`, :meth:`!__open_w__`, and
    :meth:`~WritablePath.__open_wb__` methods on the given path object as
    appropriate for the given mode.


Protocols
---------

This package offers the following protocols:

.. class:: PathParser

   Protocol for path parser objects, which split and join string paths.

   Subclasses of :class:`JoinablePath` should provide a path parser object as
   an attribute named :attr:`~JoinablePath.parser`.

   Path parsers provide a subset of the ``os.path`` API. Python itself
   provides the ``posixpath`` and ``ntpath`` modules, which can be assigned
   to :attr:`~JoinablePath.parser` to implement path objects with POSIX or
   Windows syntax.

   .. attribute:: sep

      Character used to separate path components.

   .. attribute:: altsep

      Alternative path separator character, or ``None``.

   .. method:: split(path)

      Split the path into a pair ``(head, tail)``, where *head* is
      everything before the final path separator, and *tail* is everything
      after. Either part may be empty.

      .. note::

         Trailing slashes are meaningful in ``posixpath`` and ``ntpath``, so
         ``P('foo/').parent`` is ``P('foo')``, and its
         :attr:`~JoinablePath.name` is the empty string.

   .. method:: splitext(name)

      Split the filename into a pair ``(stem, ext)``, where *ext* is a file
      extension beginning with a dot and containing at most one dot, and
      *stem* is everything before the extension.

   .. method:: normcase(path)

      Return the path with its case normalized.

      .. note::

         This method is used to detect case sensitivity in
         :meth:`JoinablePath.full_match` and :meth:`ReadablePath.glob`, where
         it's called with the string containing a mix of upper and lowercase
         letters. Case-sensitive filesystems should return the string
         unchanged, whereas case-insensitive filesystems should return the
         string with its case modified (e.g. with ``upper()`` or ``lower()``.)


.. class:: PathInfo

   Protocol for path information objects, which provide file type info.

   Subclasses of :class:`ReadablePath` should provide a path information
   object as an attribute named :attr:`~ReadablePath.info`.

   .. method:: exists(*, follow_symlinks=True)

      Return ``True`` if the path is an existing file or directory, or any
      other kind of file; return ``False`` if the path doesn't exist.

      If *follow_symlinks* is ``False``, return ``True`` for symlinks without
      checking if their targets exist.

   .. method:: is_dir(*, follow_symlinks=True)

      Return ``True`` if the path is a directory, or a symbolic link pointing
      to a directory; return ``False`` if the path is (or points to) any other
      kind of file, or if it doesn't exist.

      If *follow_symlinks* is ``False``, return ``True`` only if the path
      is a directory (without following symlinks); return ``False`` if the
      path is any other kind of file, or if it doesn't exist.

   .. method:: is_file(*, follow_symlinks=True)

      Return ``True`` if the path is a file, or a symbolic link pointing to
      a file; return ``False`` if the path is (or points to) a directory or
      other non-file, or if it doesn't exist.

      If *follow_symlinks* is ``False``, return ``True`` only if the path
      is a file (without following symlinks); return ``False`` if the path
      is a directory or other other non-file, or if it doesn't exist.

   .. method:: is_symlink()

      Return ``True`` if the path is a symbolic link (even if broken); return
      ``False`` if the path is a directory or any kind of file, or if it
      doesn't exist.


Abstract base classes
---------------------

This package offers the following abstract base classes:

.. list-table::
   :header-rows: 1

   - * ABC
     * Inherits from
     * Abstract methods
     * Mixin methods

   - * :class:`JoinablePath`
     *
     * :attr:`~JoinablePath.parser`

       :meth:`~JoinablePath.__str__`

       :meth:`~JoinablePath.with_segments`
     * :attr:`~JoinablePath.parts`
       :attr:`~JoinablePath.anchor`

       :attr:`~JoinablePath.parent`
       :attr:`~JoinablePath.parents`

       :attr:`~JoinablePath.name`
       :attr:`~JoinablePath.stem`
       :attr:`~JoinablePath.suffix`
       :attr:`~JoinablePath.suffixes`

       :meth:`~JoinablePath.with_name`
       :meth:`~JoinablePath.with_stem`
       :meth:`~JoinablePath.with_suffix`

       :meth:`~JoinablePath.joinpath`
       :meth:`~JoinablePath.__truediv__`
       :meth:`~JoinablePath.__rtruediv__`

       :meth:`~JoinablePath.full_match`

   - * :class:`ReadablePath`
     * :class:`JoinablePath`
     * :attr:`~ReadablePath.info`

       :meth:`~ReadablePath.__open_rb__`

       :meth:`~ReadablePath.iterdir`

       :meth:`~ReadablePath.readlink`
     * :meth:`~ReadablePath.read_bytes`
       :meth:`~ReadablePath.read_text`

       :meth:`~ReadablePath.copy`
       :meth:`~ReadablePath.copy_into`

       :meth:`~ReadablePath.glob`

       :meth:`~ReadablePath.walk`

   - * :class:`WritablePath`
     * :class:`JoinablePath`
     * :meth:`~WritablePath.__open_wb__`

       :meth:`~WritablePath.mkdir`

       :meth:`~WritablePath.symlink_to`
     * :meth:`~WritablePath.write_bytes`
       :meth:`~WritablePath.write_text`

       :meth:`~WritablePath._copy_from`


.. class:: JoinablePath

   Abstract base class for path objects without I/O support.

   .. attribute:: parser

      (**Abstract attribute**.) Implementation of :class:`PathParser` used for
      low-level splitting and joining.

   .. method:: __str__()

      (**Abstract method**.) Return a string representation of the path,
      suitable for passing to methods of the :attr:`parser`.

   .. method:: with_segments(*pathsegments)

      (**Abstract method**.) Create a new path object of the same type by
      combining the given *pathsegments*. This method is called whenever a
      derivative path is created, such as from :attr:`parent` and
      :meth:`with_name`.

   .. attribute:: parts

      Tuple of path components. The default implementation repeatedly calls
      :meth:`PathParser.split` to decompose the path.

   .. attribute:: anchor

      The path's irreducible prefix. The default implementation repeatedly
      calls :meth:`PathParser.split` until the directory name stops changing.

   .. attribute:: parent

      The path's lexical parent. The default implementation calls
      :meth:`PathParser.split` once.

   .. attribute:: parents

      Sequence of the path's lexical parents, beginning with the immediate
      parent. The default implementation repeatedly calls
      :meth:`PathParser.split`.

   .. attribute:: name

      The path's base name. The name is empty if the path has only an anchor,
      or ends with a slash. The default implementation calls
      :meth:`PathParser.split` once.

   .. attribute:: stem

      The path's base name with the file extension omitted. The default
      implementation calls :meth:`PathParser.splitext` on :attr:`name`.

   .. attribute:: suffix

      The path's file extension. The default implementation calls
      :meth:`PathParser.splitext` on :attr:`name`.

   .. attribute:: suffixes

      Sequence of the path's file extensions. The default implementation
      repeatedly calls :meth:`PathParser.splitext` on :attr:`name`.

   .. method:: with_name(name)

      Return a new path with a different :attr:`name`. The name may be empty.
      The default implementation calls :meth:`PathParser.split` to remove the
      old name, and :meth:`with_segments` to create the new path object.

   .. method:: with_stem(stem)

      Return a new path with a different :attr:`stem`, similarly to
      :meth:`with_name`.

   .. method:: with_suffix(suffix)

      Return a new path with a different :attr:`suffix`, similarly to
      :meth:`with_name`.

   .. method:: joinpath(*pathsegments)

      Return a new path with the given path segments joined onto the end. The
      default implementation calls :meth:`with_segments` with the combined
      segments.

   .. method:: __truediv__(pathsegment)

      Return a new path with the given path segment joined on the end.

   .. method:: __rtruediv__(pathsegment)

      Return a new path with the given path segment joined on the beginning.

   .. method:: full_match(pattern)

      Return true if the path matches the given glob-style pattern, false
      otherwise. The default implementation uses :meth:`PathParser.normcase`
      to establish case sensitivity.


.. class:: ReadablePath

   Abstract base class for path objects with support for reading data. This
   is a subclass of :class:`JoinablePath`

   .. attribute:: info

      (**Abstract attribute**.) Implementation of :class:`PathInfo` that
      supports querying the file type.

   .. method:: __open_rb__(buffering=-1)

      (**Abstract method.**) Open the path for reading in binary mode, and
      return a file object.

   .. method:: iterdir()

      (**Abstract method**.) Yield path objects for the directory contents.

   .. method:: readlink()

      (**Abstract method**.) Return the symlink target as a new path object.

   .. method:: read_bytes()

      Return the binary contents of the path. The default implementation
      calls :meth:`__open_rb__`.

   .. method:: read_text(encoding=None, errors=None, newline=None)

      Return the text contents of the path. The default implementation calls
      :meth:`!__open_r__` if it exists, falling back to :meth:`__open_rb__`.

   .. method:: copy(target, **kwargs)

      Copy the path to the given target, which should be an instance of
      :class:`WritablePath`. The default implementation calls
      :meth:`WritablePath._copy_from`, passing along keyword arguments.

   .. method:: copy_into(target_dir, **kwargs)

      Copy the path *into* the given target directory, which should be an
      instance of :class:`WritablePath`. See :meth:`copy`.

   .. method:: glob(pattern, *, recurse_symlinks=True)

      Yield path objects in the file tree that match the given glob-style
      pattern. The default implementation uses :attr:`info` and
      :meth:`iterdir`.

      .. warning::

         For performance reasons, the default value for *recurse_symlinks* is
         ``True`` in this base class, but for historical reasons, the default
         is ``False`` in ``pathlib.Path``. Furthermore, ``True`` is the *only*
         acceptable value for *recurse_symlinks* in this base class.

         For maximum compatibility, users should supply
         ``recurse_symlinks=True`` explicitly when globbing recursively.

   .. method:: walk(top_down=True, on_error=None, follow_symlinks=False)

      Yield a ``(dirpath, dirnames, filenames)`` triplet for each directory
      in the file tree, like ``os.walk()``. The default implementation uses
      :attr:`info` and :meth:`iterdir`.


.. class:: WritablePath

   Abstract base class for path objects with support for writing data. This
   is a subclass of :class:`JoinablePath`

   .. method:: __open_wb__(buffering=-1)

      (**Abstract method**.) Open the path for writing in binary mode, and
      return a file object.

   .. method:: mkdir()

      (**Abstract method**.) Create this path as a directory.

   .. method:: symlink_to(target, target_is_directory=False)

      (**Abstract method**.) Create this path as a symlink to the given
      target.

   .. method:: write_bytes(data)

      Write the given binary data to the path, and return the number of bytes
      written. The default implementation calls :meth:`__open_wb__`.

   .. method:: write_text(data, encoding=None, errors=None, newline=None)

      Write the given text data to the path, and return the number of bytes
      written. The default implementation calls :meth:`!__open_w__` if it
      exists, falling back to :meth:`__open_wb__`.

   .. method:: _copy_from(source, *, follow_symlinks=True)

      Copy the path from the given source, which should be an instance of
      :class:`ReadablePath`. The default implementation uses
      :attr:`ReadablePath.info` to establish the type of the source path. It
      uses :meth:`~ReadablePath.__open_rb__` and :meth:`__open_wb__` to copy
      regular files; :meth:`~ReadablePath.iterdir` and :meth:`mkdir` to copy
      directories; and :meth:`~ReadablePath.readlink` and :meth:`symlink_to`
      to copy symlinks when *follow_symlinks* is false.
