#!/bin/bash

set -xe

cp cpython/Lib/pathlib/_abc.py                       pathlib_abc/__init__.py
cp cpython/Lib/test/test_pathlib/test_pathlib_abc.py tests/test_pathlib_abc.py

patch -p1 < sync.patch
