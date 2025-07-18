"""
This type stub file was generated by pyright.
"""

import numpy as np
from collections.abc import Hashable, Iterator
from typing import Any, Callable, Literal, TYPE_CHECKING, overload
from pandas.util._decorators import cache_readonly, deprecate_nonkeyword_arguments, doc
from pandas.core.indexes.base import Index
from pandas.core.ops.common import unpack_zerodim_and_defer
from pandas._typing import Axis, Dtype, NaPosition, Self, npt

if TYPE_CHECKING:
    ...
_empty_range = ...
_dtype_int64 = ...

class RangeIndex(Index):
    """
    Immutable Index implementing a monotonic integer range.

    RangeIndex is a memory-saving special case of an Index limited to representing
    monotonic ranges with a 64-bit dtype. Using RangeIndex may in some instances
    improve computing speed.

    This is the default index type used
    by DataFrame and Series when no explicit index is provided by the user.

    Parameters
    ----------
    start : int (default: 0), range, or other RangeIndex instance
        If int and "stop" is not given, interpreted as "stop" instead.
    stop : int (default: 0)
    step : int (default: 1)
    dtype : np.int64
        Unused, accepted for homogeneity with other index types.
    copy : bool, default False
        Unused, accepted for homogeneity with other index types.
    name : object, optional
        Name to be stored in the index.

    Attributes
    ----------
    start
    stop
    step

    Methods
    -------
    from_range

    See Also
    --------
    Index : The base pandas Index type.

    Examples
    --------
    >>> list(pd.RangeIndex(5))
    [0, 1, 2, 3, 4]

    >>> list(pd.RangeIndex(-2, 4))
    [-2, -1, 0, 1, 2, 3]

    >>> list(pd.RangeIndex(0, 10, 2))
    [0, 2, 4, 6, 8]

    >>> list(pd.RangeIndex(2, -10, -3))
    [2, -1, -4, -7]

    >>> list(pd.RangeIndex(0))
    []

    >>> list(pd.RangeIndex(1, 0))
    []
    """

    _typ = ...
    _dtype_validation_metadata = ...
    _range: range
    _values: np.ndarray
    def __new__(
        cls,
        start=...,
        stop=...,
        step=...,
        dtype: Dtype | None = ...,
        copy: bool = ...,
        name: Hashable | None = ...,
    ) -> Self: ...
    @classmethod
    def from_range(cls, data: range, name=..., dtype: Dtype | None = ...) -> Self:
        """
        Create :class:`pandas.RangeIndex` from a ``range`` object.

        Returns
        -------
        RangeIndex

        Examples
        --------
        >>> pd.RangeIndex.from_range(range(5))
        RangeIndex(start=0, stop=5, step=1)

        >>> pd.RangeIndex.from_range(range(2, -10, -3))
        RangeIndex(start=2, stop=-10, step=-3)
        """
        ...

    def __reduce__(
        self,
    ):  # -> tuple[Callable[..., PeriodIndex | MultiIndex | Any], tuple[type[Self], dict[str, Hashable]], None]:
        ...

    @property
    def start(self) -> int:
        """
        The value of the `start` parameter (``0`` if this was not supplied).

        Examples
        --------
        >>> idx = pd.RangeIndex(5)
        >>> idx.start
        0

        >>> idx = pd.RangeIndex(2, -10, -3)
        >>> idx.start
        2
        """
        ...

    @property
    def stop(self) -> int:
        """
        The value of the `stop` parameter.

        Examples
        --------
        >>> idx = pd.RangeIndex(5)
        >>> idx.stop
        5

        >>> idx = pd.RangeIndex(2, -10, -3)
        >>> idx.stop
        -10
        """
        ...

    @property
    def step(self) -> int:
        """
        The value of the `step` parameter (``1`` if this was not supplied).

        Examples
        --------
        >>> idx = pd.RangeIndex(5)
        >>> idx.step
        1

        >>> idx = pd.RangeIndex(2, -10, -3)
        >>> idx.step
        -3

        Even if :class:`pandas.RangeIndex` is empty, ``step`` is still ``1`` if
        not supplied.

        >>> idx = pd.RangeIndex(1, 0)
        >>> idx.step
        1
        """
        ...

    @cache_readonly
    def nbytes(self) -> int:
        """
        Return the number of bytes in the underlying data.
        """
        ...

    def memory_usage(self, deep: bool = ...) -> int:
        """
        Memory usage of my values

        Parameters
        ----------
        deep : bool
            Introspect the data deeply, interrogate
            `object` dtypes for system-level memory consumption

        Returns
        -------
        bytes used

        Notes
        -----
        Memory usage does not include memory consumed by elements that
        are not components of the array if deep=False

        See Also
        --------
        numpy.ndarray.nbytes
        """
        ...

    @property
    def dtype(self) -> np.dtype: ...
    @property
    def is_unique(self) -> bool:
        """return if the index has unique values"""
        ...

    @cache_readonly
    def is_monotonic_increasing(self) -> bool: ...
    @cache_readonly
    def is_monotonic_decreasing(self) -> bool: ...
    def __contains__(self, key: Any) -> bool: ...
    @property
    def inferred_type(self) -> str: ...
    @doc(Index.get_loc)
    def get_loc(self, key) -> int: ...
    def tolist(self) -> list[int]: ...
    @doc(Index.__iter__)
    def __iter__(self) -> Iterator[int]: ...
    @doc(Index.copy)
    def copy(self, name: Hashable | None = ..., deep: bool = ...) -> Self: ...
    def min(self, axis=..., skipna: bool = ..., *args, **kwargs) -> int:
        """The minimum value of the RangeIndex"""
        ...

    def max(self, axis=..., skipna: bool = ..., *args, **kwargs) -> int:
        """The maximum value of the RangeIndex"""
        ...

    def argsort(self, *args, **kwargs) -> npt.NDArray[np.intp]:
        """
        Returns the indices that would sort the index and its
        underlying data.

        Returns
        -------
        np.ndarray[np.intp]

        See Also
        --------
        numpy.ndarray.argsort
        """
        ...

    def factorize(
        self, sort: bool = ..., use_na_sentinel: bool = ...
    ) -> tuple[npt.NDArray[np.intp], RangeIndex]: ...
    def equals(self, other: object) -> bool:
        """
        Determines if two Index objects contain the same elements.
        """
        ...

    @overload
    def sort_values(
        self,
        *,
        return_indexer: Literal[False] = ...,
        ascending: bool = ...,
        na_position: NaPosition = ...,
        key: Callable | None = ...
    ) -> Self: ...
    @overload
    def sort_values(
        self,
        *,
        return_indexer: Literal[True],
        ascending: bool = ...,
        na_position: NaPosition = ...,
        key: Callable | None = ...
    ) -> tuple[Self, np.ndarray | RangeIndex]: ...
    @overload
    def sort_values(
        self,
        *,
        return_indexer: bool = ...,
        ascending: bool = ...,
        na_position: NaPosition = ...,
        key: Callable | None = ...
    ) -> Self | tuple[Self, np.ndarray | RangeIndex]: ...
    @deprecate_nonkeyword_arguments(
        version="3.0", allowed_args=["self"], name="sort_values"
    )
    def sort_values(
        self,
        return_indexer: bool = ...,
        ascending: bool = ...,
        na_position: NaPosition = ...,
        key: Callable | None = ...,
    ) -> Self | tuple[Self, np.ndarray | RangeIndex]: ...
    def symmetric_difference(
        self, other, result_name: Hashable | None = ..., sort=...
    ):  # -> Self | Index | MultiIndex:
        ...

    def delete(self, loc) -> Index: ...
    def insert(self, loc: int, item) -> Index: ...
    def __len__(self) -> int:
        """
        return the length of the RangeIndex
        """
        ...

    @property
    def size(self) -> int: ...
    def __getitem__(self, key):  # -> Self | int:
        """
        Conserve RangeIndex type for scalar and slice keys.
        """
        ...

    @unpack_zerodim_and_defer("__floordiv__")
    def __floordiv__(self, other):  # -> Self | _NotImplementedType:
        ...

    def all(self, *args, **kwargs) -> bool: ...
    def any(self, *args, **kwargs) -> bool: ...
    def take(
        self,
        indices,
        axis: Axis = ...,
        allow_fill: bool = ...,
        fill_value=...,
        **kwargs
    ) -> Index: ...
