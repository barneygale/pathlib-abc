import errno
import os
import stat


def _realpath(filename, strict=False, sep='/', curdir='.', pardir='..',
              getcwd=os.getcwd, lstat=os.lstat, readlink=os.readlink, maxlinks=None):
    # The stack of unresolved path parts. When popped, a special value of None
    # indicates that a symlink target has been resolved, and that the original
    # symlink path can be retrieved by popping again. The [::-1] slice is a
    # very fast way of spelling list(reversed(...)).
    rest = filename.split(sep)[::-1]

    # The resolved path, which is absolute throughout this function.
    # Note: getcwd() returns a normalized and symlink-free path.
    path = sep if filename.startswith(sep) else getcwd()

    # Mapping from symlink paths to *fully resolved* symlink targets. If a
    # symlink is encountered but not yet resolved, the value is None. This is
    # used both to detect symlink loops and to speed up repeated traversals of
    # the same links.
    seen = {}

    # Number of symlinks traversed. When the number of traversals is limited
    # by *maxlinks*, this is used instead of *seen* to detect symlink loops.
    link_count = 0

    while rest:
        name = rest.pop()
        if name is None:
            # resolved symlink target
            seen[rest.pop()] = path
            continue
        if not name or name == curdir:
            # current dir
            continue
        if name == pardir:
            # parent dir
            path = path[:path.rindex(sep)] or sep
            continue
        if path == sep:
            newpath = path + name
        else:
            newpath = path + sep + name
        try:
            st = lstat(newpath)
            if not stat.S_ISLNK(st.st_mode):
                path = newpath
                continue
            elif maxlinks is not None:
                link_count += 1
                if link_count > maxlinks:
                    if strict:
                        raise OSError(errno.ELOOP, os.strerror(errno.ELOOP),
                                      newpath)
                    path = newpath
                    continue
            elif newpath in seen:
                # Already seen this path
                path = seen[newpath]
                if path is not None:
                    # use cached value
                    continue
                # The symlink is not resolved, so we must have a symlink loop.
                if strict:
                    raise OSError(errno.ELOOP, os.strerror(errno.ELOOP),
                                  newpath)
                path = newpath
                continue
            target = readlink(newpath)
        except OSError:
            if strict:
                raise
            path = newpath
            continue
        # Resolve the symbolic link
        if target.startswith(sep):
            # Symlink target is absolute; reset resolved path.
            path = sep
        if maxlinks is None:
            # Mark this symlink as seen but not fully resolved.
            seen[newpath] = None
            # Push the symlink path onto the stack, and signal its specialness
            # by also pushing None. When these entries are popped, we'll
            # record the fully-resolved symlink target in the 'seen' mapping.
            rest.append(newpath)
            rest.append(None)
        # Push the unresolved symlink target parts onto the stack.
        rest.extend(target.split(sep)[::-1])

    return path
