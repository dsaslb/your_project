"""
This type stub file was generated by pyright.
"""

from typing import TYPE_CHECKING

"""
Core eval alignment algorithms.
"""
if TYPE_CHECKING:
    ...

def align_terms(
    terms,
):  # -> tuple[type[Series] | type[DataFrame], dict[str, Index]] | tuple[dtype[Any], None] | tuple[type[Any], None] | tuple[Any, Any]:
    """
    Align a set of terms.
    """
    ...

def reconstruct_object(
    typ, obj, axes, dtype
):  # -> PandasObject | Any | ndarray[_Shape, dtype[Any]]:
    """
    Reconstruct an object given its type, raw value, and possibly empty
    (None) axes.

    Parameters
    ----------
    typ : object
        A type
    obj : object
        The value to use in the type constructor
    axes : dict
        The axes to use to construct the resulting pandas object

    Returns
    -------
    ret : typ
        An object of type ``typ`` with the value `obj` and possible axes
        `axes`.
    """
    ...
