"""
This type stub file was generated by pyright.
"""

import numpy as np
from pandas._typing import npt

def calculate_variable_window_bounds(
    num_values: int,
    window_size: int,
    min_periods,
    center: bool,
    closed: str | None,
    index: np.ndarray,
) -> tuple[npt.NDArray[np.int64], npt.NDArray[np.int64]]: ...
