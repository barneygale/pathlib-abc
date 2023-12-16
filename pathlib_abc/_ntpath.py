import os
from ntpath import sep, altsep, join, normcase, splitdrive


def splitroot(p):
    """Split a pathname into drive, root and tail. The drive is defined
    exactly as in splitdrive(). On Windows, the root may be a single path
    separator or an empty string. The tail contains anything after the root.
    For example:

        splitroot('//server/share/') == ('//server/share', '/', '')
        splitroot('C:/Users/Barney') == ('C:', '/', 'Users/Barney')
        splitroot('C:///spam///ham') == ('C:', '/', '//spam///ham')
        splitroot('Windows/notepad') == ('', '', 'Windows/notepad')
    """
    p = os.fspath(p)
    if isinstance(p, bytes):
        sep = b'\\'
        altsep = b'/'
        colon = b':'
        unc_prefix = b'\\\\?\\UNC\\'
        empty = b''
    else:
        sep = '\\'
        altsep = '/'
        colon = ':'
        unc_prefix = '\\\\?\\UNC\\'
        empty = ''
    normp = p.replace(altsep, sep)
    if normp[:1] == sep:
        if normp[1:2] == sep:
            # UNC drives, e.g. \\server\share or \\?\UNC\server\share
            # Device drives, e.g. \\.\device or \\?\device
            start = 8 if normp[:8].upper() == unc_prefix else 2
            index = normp.find(sep, start)
            if index == -1:
                return p, empty, empty
            index2 = normp.find(sep, index + 1)
            if index2 == -1:
                return p, empty, empty
            return p[:index2], p[index2:index2 + 1], p[index2 + 1:]
        else:
            # Relative path with root, e.g. \Windows
            return empty, p[:1], p[1:]
    elif normp[1:2] == colon:
        if normp[2:3] == sep:
            # Absolute drive-letter path, e.g. X:\Windows
            return p[:2], p[2:3], p[3:]
        else:
            # Relative path with drive, e.g. X:Windows
            return p[:2], empty, p[2:]
    else:
        # Relative path, e.g. Windows
        return empty, empty, p
