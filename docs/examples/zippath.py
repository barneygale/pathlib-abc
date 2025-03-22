import posixpath

from pathlib_abc import PathInfo, ReadablePath


class MissingInfo(PathInfo):
    __slots__ = ()

    def exists(self, follow_symlinks=True): return False
    def is_dir(self, follow_symlinks=True): return False
    def is_file(self, follow_symlinks=True): return False
    def is_symlink(self): return False


class ZipPathInfo(PathInfo):
    __slots__ = ('zip_info', 'children')

    def __init__(self):
        self.zip_info = None
        self.children = {}

    def exists(self, follow_symlinks=True):
        return True

    def is_dir(self, follow_symlinks=True):
        if self.zip_info is None:
            return True
        else:
            return self.zip_info.filename.endswith('/')

    def is_file(self, follow_symlinks=True):
        if self.zip_info is None:
            return False
        else:
            return not self.zip_info.filename.endswith('/')

    def is_symlink(self):
        return False

    def resolve(self, path, create=False):
        if not path:
            return self
        name, _, path = path.partition('/')
        if not name:
            info = self
        elif name in self.children:
            info = self.children[name]
        elif create:
            info = self.children[name] = ZipPathInfo()
        else:
            return MissingInfo()
        return info.resolve(path, create)


class ZipPath(ReadablePath):
    __slots__ = ('_segments', 'zip_file')
    parser = posixpath

    def __init__(self, *pathsegments, zip_file):
        self._segments = pathsegments
        self.zip_file = zip_file
        if not hasattr(zip_file, 'filetree'):
            # Read the contents into a tree of ZipPathInfo objects.
            zip_file.filetree = ZipPathInfo()
            for zip_info in zip_file.filelist:
                info = zip_file.filetree.resolve(zip_info.filename, create=True)
                info.zip_info = zip_info

    def __str__(self):
        if not self._segments:
            return ''
        return self.parser.join(*self._segments)

    def with_segments(self, *pathsegments):
        return type(self)(*pathsegments, zip_file=self.zip_file)

    @property
    def info(self):
        return self.zip_file.filetree.resolve(str(self))

    def __open_rb__(self, buffering=-1):
        return self.zip_file.open(self.info.zip_info, 'r')

    def iterdir(self):
        return (self / name for name in self.info.children)

    def readlink(self):
        raise NotImplementedError
