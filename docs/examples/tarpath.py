import collections
import posixpath
import tarfile
import errno
import io
import stat

from pathlib_abc import PathBase, UnsupportedOperation

_tar_stat_fields = ('st_mode st_ino st_dev st_nlink st_uid st_gid '
                    'st_size st_atime st_mtime st_ctime st_uname st_gname')


class TarStatResult(collections.namedtuple('_TarStatResult', _tar_stat_fields)):
    """Tar-specific version of os.stat_result. Returned by TarPath.stat()."""
    __slots__ = ()

    @classmethod
    def from_tarinfo(cls, tarobj, tarinfo):
        """Create a TarStatResult from TarFile and TarInfo objects."""
        if tarinfo.type in tarfile.REGULAR_TYPES:
            st_mode = stat.S_IFREG
        elif tarinfo.type == tarfile.DIRTYPE:
            st_mode = stat.S_IFDIR
        elif tarinfo.type == tarfile.SYMTYPE or tarinfo.type == tarfile.LNKTYPE:
            st_mode = stat.S_IFLNK
        elif tarinfo.type == tarfile.FIFOTYPE:
            st_mode = stat.S_IFIFO
        elif tarinfo.type == tarfile.CHRTYPE:
            st_mode = stat.S_IFCHR
        elif tarinfo.type == tarfile.BLKTYPE:
            st_mode = stat.S_IFBLK
        else:
            raise ValueError(tarinfo.type)
        return cls(st_mode=tarinfo.mode | st_mode,
                   st_ino=tarinfo.offset_data,
                   st_dev=id(tarobj),
                   st_nlink=0,
                   st_uid=tarinfo.uid,
                   st_gid=tarinfo.gid,
                   st_size=tarinfo.size,
                   st_atime=0,
                   st_mtime=tarinfo.mtime,
                   st_ctime=0,
                   st_uname=tarinfo.uname,
                   st_gname=tarinfo.gname)

    @classmethod
    def implied_directory(cls, tarobj, path):
        """Create a TarStatResult for a directory that is implied to exist
           by another archive member's path.
        """
        return cls(stat.S_IFDIR, hash(path), id(tarobj), 0, 0, 0, 0, 0, 0, 0, None, None)


class TarPathWriter(io.BytesIO):
    """File object that flushes its contents to a tar archive on close.
       Returned by TarPath.open(mode="w").
    """

    def __init__(self, tarobj, path):
        super().__init__()
        self.tarobj = tarobj
        self.path = path

    def close(self):
        info = tarfile.TarInfo(self.path)
        info.size = self.tell()
        self.seek(0)
        self.tarobj.addfile(info, self)
        super().close()


class TarPath(PathBase):
    """A pathlib-compatible interface for tar files."""

    __slots__ = ('tarobj',)
    parser = posixpath

    def __init__(self, *pathsegments, tarobj):
        super().__init__(*pathsegments)
        self.tarobj = tarobj

    def __repr__(self):
        return f"{type(self).__name__}({str(self)!r}, tarobj={self.tarobj!r})"

    def __hash__(self):
        return hash((id(self.tarobj), str(self)))

    def __eq__(self, other):
        if not isinstance(other, TarPath):
            return NotImplemented
        return self.tarobj is other.tarobj and str(self) == str(other)

    def with_segments(self, *pathsegments):
        """Construct a new TarPath object with the same underlying TarFile
           object from any number of path-like objects.
        """
        return type(self)(*pathsegments, tarobj=self.tarobj)

    def stat(self, *, follow_symlinks=True):
        """Return the path's status, similar to os.stat()."""
        if follow_symlinks:
            resolved = self.resolve()
        else:
            resolved = self.parent.resolve() / self.name
        implied_directory = False
        for info in reversed(self.tarobj.getmembers()):
            path = self.with_segments(info.name)
            if path == resolved:
                return TarStatResult.from_tarinfo(self.tarobj, info)
            elif resolved in path.parents:
                implied_directory = True
        if implied_directory:
            return TarStatResult.implied_directory(self.tarobj, str(resolved))
        else:
            raise FileNotFoundError(errno.ENOENT, "Not found", str(self))

    def owner(self, *, follow_symlinks=True):
        """Return the user name of the path owner."""
        name = self.stat(follow_symlinks=follow_symlinks).st_uname
        if name is not None:
            return name
        raise UnsupportedOperation()

    def group(self, *, follow_symlinks=True):
        """Return the group name of the path owner."""
        name = self.stat(follow_symlinks=follow_symlinks).st_gname
        if name is not None:
            return name
        raise UnsupportedOperation()

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        """Open the archive member pointed by this path and return a file
           object, similar to the built-in open() function.
        """
        if buffering != -1:
            raise UnsupportedOperation()
        action = ''.join(c for c in mode if c not in 'btU')
        if action == 'r':
            fileobj = self.tarobj.extractfile(str(self.resolve()))
        elif action == 'w':
            fileobj = TarPathWriter(self.tarobj, str(self.resolve()))
        else:
            raise UnsupportedOperation()
        if 'b' not in mode:
            fileobj = io.TextIOWrapper(fileobj, encoding, errors, newline)
        return fileobj

    def iterdir(self):
        """Yield path objects of the directory contents. The children are
           yielded in arbitrary order.
        """
        resolved = self.resolve()
        seen = set()
        for info in self.tarobj.getmembers():
            path = self.with_segments(info.name)
            if path == resolved:
                if info.type != tarfile.DIRTYPE:
                    raise NotADirectoryError(errno.ENOTDIR, "Not a directory", str(self))
            while True:
                parent = path.parent
                if parent == path:
                    break
                elif parent == resolved:
                    path_str = str(path)
                    if path_str not in seen:
                        seen.add(path_str)
                        yield self / path.name
                    break
                path = parent
        if not seen:
            raise FileNotFoundError(errno.ENOENT, "File not found", str(self))

    def readlink(self):
        """Return the path to which the symbolic link points."""
        for info in reversed(self.tarobj.getmembers()):
            path = self.with_segments(info.name)
            if path == self:
                if info.issym():
                    return self.with_segments(info.linkname)
                else:
                    raise OSError(errno.EINVAL, "Not a symlink", str(self))
            elif self in path.parents:
                raise OSError(errno.EINVAL, "Not a symlink", str(self))
        raise FileNotFoundError(errno.ENOENT, "File not found", str(self))

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """Create a new directory at this given path."""
        info = tarfile.TarInfo(str(self))
        info.type = tarfile.DIRTYPE
        info.mode = mode
        self.tarobj.addfile(info)

    def symlink_to(self, target, target_is_directory=False):
        """Make this path a symlink pointing to the target path."""
        info = tarfile.TarInfo(str(self))
        info.type = tarfile.SYMTYPE
        info.linkname = str(self.with_segments(target))
        self.tarobj.addfile(info)

    def hardlink_to(self, target):
        """Make this path a hard link pointing to the target path."""
        info = tarfile.TarInfo(str(self))
        info.type = tarfile.LNKTYPE
        info.linkname = str(self.with_segments(target))
        self.tarobj.addfile(info)
