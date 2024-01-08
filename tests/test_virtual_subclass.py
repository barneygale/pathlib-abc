from pathlib import PurePath, PurePosixPath, PureWindowsPath, Path
from pathlib_abc import PathBase, PurePathBase

import pytest


@pytest.mark.parametrize("cls", [PurePath, PurePosixPath, PureWindowsPath, Path])
def test_virtual_subclass_purepath(cls):
    assert issubclass(cls, PurePathBase)
    assert isinstance(cls(), PurePathBase)


def test_virtual_subclass_path():
    assert issubclass(Path, PathBase)
    assert isinstance(Path(), PathBase)
