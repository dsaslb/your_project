"""
This type stub file was generated by pyright.
"""

import numpy as np
from pandas._typing import npt

def array_strptime(
    values: npt.NDArray[np.object_],
    fmt: str | None,
    exact: bool = ...,
    errors: str = ...,
    utc: bool = ...,
    creso: int = ...,
) -> tuple[np.ndarray, np.ndarray]: ...
