"""
This type stub file was generated by pyright.
"""

from typing import Any, TYPE_CHECKING
from pandas._typing import ArrayLike

"""
Functions for defining unary operations.
"""
if TYPE_CHECKING:
    ...

def should_extension_dispatch(left: ArrayLike, right: Any) -> bool:
    """
    Identify cases where Series operation should dispatch to ExtensionArray method.

    Parameters
    ----------
    left : np.ndarray or ExtensionArray
    right : object

    Returns
    -------
    bool
    """
    ...
