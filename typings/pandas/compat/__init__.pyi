"""
This type stub file was generated by pyright.
"""

import os
import platform
import sys
import pandas.compat.compressors
from typing import TYPE_CHECKING
from pandas.compat._constants import IS64, ISMUSL, PY310, PY311, PY312, PYPY
from pandas.compat.numpy import is_numpy_dev
from pandas.compat.pyarrow import (
    HAS_PYARROW,
    pa_version_under10p1,
    pa_version_under11p0,
    pa_version_under13p0,
    pa_version_under14p0,
    pa_version_under14p1,
    pa_version_under16p0,
    pa_version_under17p0,
    pa_version_under18p0,
    pa_version_under19p0,
    pa_version_under20p0,
    pa_version_under21p0,
)
from pandas._typing import F

"""
compat
======

Cross-compatible functions for different versions of Python.

Other items:
* platform checker
"""
if TYPE_CHECKING:
    ...

def set_function_name(f: F, name: str, cls: type) -> F:
    """
    Bind the name/qualname attributes of the function.
    """
    ...

def is_platform_little_endian() -> bool:
    """
    Checking if the running platform is little endian.

    Returns
    -------
    bool
        True if the running platform is little endian.
    """
    ...

def is_platform_windows() -> bool:
    """
    Checking if the running platform is windows.

    Returns
    -------
    bool
        True if the running platform is windows.
    """
    ...

def is_platform_linux() -> bool:
    """
    Checking if the running platform is linux.

    Returns
    -------
    bool
        True if the running platform is linux.
    """
    ...

def is_platform_mac() -> bool:
    """
    Checking if the running platform is mac.

    Returns
    -------
    bool
        True if the running platform is mac.
    """
    ...

def is_platform_arm() -> bool:
    """
    Checking if the running platform use ARM architecture.

    Returns
    -------
    bool
        True if the running platform uses ARM architecture.
    """
    ...

def is_platform_power() -> bool:
    """
    Checking if the running platform use Power architecture.

    Returns
    -------
    bool
        True if the running platform uses ARM architecture.
    """
    ...

def is_ci_environment() -> bool:
    """
    Checking if running in a continuous integration environment by checking
    the PANDAS_CI environment variable.

    Returns
    -------
    bool
        True if the running in a continuous integration environment.
    """
    ...

def get_lzma_file() -> type[pandas.compat.compressors.LZMAFile]:
    """
    Importing the `LZMAFile` class from the `lzma` module.

    Returns
    -------
    class
        The `LZMAFile` class from the `lzma` module.

    Raises
    ------
    RuntimeError
        If the `lzma` module was not imported correctly, or didn't exist.
    """
    ...

def get_bz2_file() -> type[pandas.compat.compressors.BZ2File]:
    """
    Importing the `BZ2File` class from the `bz2` module.

    Returns
    -------
    class
        The `BZ2File` class from the `bz2` module.

    Raises
    ------
    RuntimeError
        If the `bz2` module was not imported correctly, or didn't exist.
    """
    ...

__all__ = [
    "is_numpy_dev",
    "pa_version_under10p1",
    "pa_version_under11p0",
    "pa_version_under13p0",
    "pa_version_under14p0",
    "pa_version_under14p1",
    "pa_version_under16p0",
    "pa_version_under17p0",
    "pa_version_under18p0",
    "pa_version_under19p0",
    "pa_version_under20p0",
    "pa_version_under21p0",
    "HAS_PYARROW",
    "IS64",
    "ISMUSL",
    "PY310",
    "PY311",
    "PY312",
    "PYPY",
]
