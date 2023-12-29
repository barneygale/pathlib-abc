API Reference
=============


Exceptions
----------

.. exception:: UnsupportedOperation

   An exception inheriting :exc:`NotImplementedError` that is raised when an
   unsupported operation is called on a path object.


Base classes
------------

.. class:: PurePathBase(*pathsegments)

   Abstract base class for path objects without I/O support.

   Not properly documented yet.

.. class:: PathBase(*pathsegments)

   Abstract base class for path objects with I/O support.

   This class provides abstract implementations for methods that derived
   classes can override selectively. The default implementations of the most
   basic methods, like :meth:`stat` and :meth:`iterdir`, directly raise
   :exc:`UnsupportedOperation`


Parsing and generating URIs
---------------------------

.. classmethod:: PathBase.from_uri(uri)

   Return a new path object from parsing a URI.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PurePath.as_uri()

   Represent the path as a URI.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.


Querying status and type
------------------------

.. method:: PathBase.stat(*, follow_symlinks=True)

   Returns information about the path. Implementations should return an object
   that resembles an ``os.stat_result`` it should at least have ``st_mode``,
   ``st_dev`` and ``st_ino`` attributes.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PathBase.lstat()
.. method:: PathBase.exists(*, follow_symlinks=True)
.. method:: PathBase.is_dir(*, follow_symlinks=True)
.. method:: PathBase.is_file(*, follow_symlinks=True)
.. method:: PathBase.is_mount()
.. method:: PathBase.is_symlink()
.. method:: PathBase.is_socket()
.. method:: PathBase.is_fifo()
.. method:: PathBase.is_block_device()
.. method:: PathBase.is_char_device()
.. method:: PathBase.samefile(other_path)

   The default implementations of these methods call :meth:`stat`.

.. method:: PathBase.is_junction()

      Returns ``True`` if the path points to a junction.

      The default implementation of this method returns ``False`` rather than
      raising :exc:`UnsupportedOperation`, because junctions are almost never
      available in virtual filesystems.


Reading and writing files
-------------------------

.. method:: PathBase.open(mode='r', buffering=-1, encoding=None, errors=None, newline=None)

   Opens the path as a file-like object.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PathBase.read_bytes()
.. method:: PathBase.read_text(encoding=None, errors=None, newline=None)
.. method:: PathBase.write_bytes(data)
.. method:: PathBase.write_text(data, encoding=None, errors=None, newline=None)

   The default implementations of these methods call :meth:`open`.


Iterating over directories
--------------------------

.. method:: PathBase.iterdir()

   Yields path objects representing directory children.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PathBase.glob(pattern, *, case_sensitive=None, follow_symlinks=None)
.. method:: PathBase.rglob(pattern, *, case_sensitive=None, follow_symlinks=None)
.. method:: PathBase.walk(top_down=True, on_error=None, follow_symlinks=False)

   The default implementations of these methods call :meth:`iterdir` and
   :meth:`is_dir`.


Making paths absolute
---------------------

.. method:: PathBase.absolute()

   Returns an absolute version of this path.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. classmethod:: PathBase.cwd()

   The default implementation of this method calls :meth:`absolute`.


Expanding home directories
--------------------------

.. method:: PathBase.expanduser()

   Return a new path with expanded ``~`` and ``~user`` constructs.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. classmethod:: PathBase.home()

   The default implementation of this method calls :meth:`expanduser`.


Resolving symlinks
------------------

.. method:: PathBase.readlink()

   Return the path to which the symbolic link points.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PathBase.resolve(strict=False)

   Resolves symlinks and eliminates ``..`` path components. If supported,
   make the path absolute.

   The default implementation of this method first calls :meth:`absolute`, but
   suppresses any resulting :exc:`UnsupportedOperation` exception; this allows
   paths to be resolved on filesystems that lack a notion of a working
   directory. It calls :meth:`stat` on each ancestor path, and
   :meth:`readlink` when a stat result indicates a symlink. :exc:`OSError` is
   raised if more than 40 symlinks are encountered while resolving a path;
   this is taken to indicate a loop.


Permissions
-----------

.. method:: PathBase.chmod(mode, *, follow_symlinks=True)

   Change the file permissions.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PathBase.lchmod(mode)

   The default implementation of this method calls :meth:`chmod`.


Ownership
---------

.. method:: PathBase.owner(*, follow_symlinks=True)

   Return the name of the user owning the file.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.

.. method:: PathBase.group(*, follow_symlinks=True)

   Return the name of the group owning the file.

   The default implementation of this method immediately raises
   :exc:`UnsupportedOperation`.


Other methods
-------------

.. method:: PathBase.symlink_to(target, target_is_directory=False)
.. method:: PathBase.hardlink_to(target)
.. method:: PathBase.touch(mode=0o666, exist_ok=True)
.. method:: PathBase.mkdir(mode=0o777, parents=False, exist_ok=False)
.. method:: PathBase.rename(target)
.. method:: PathBase.replace(target)
.. method:: PathBase.unlink(missing_ok=False)
.. method:: PathBase.rmdir()

   The default implementations of these methods immediately raise
   :exc:`UnsupportedOperation`.
