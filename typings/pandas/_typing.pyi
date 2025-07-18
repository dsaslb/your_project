"""
This type stub file was generated by pyright.
"""

import numpy as np
import numpy.typing as npt
from collections.abc import Hashable, Iterator, Mapping, MutableMapping, Sequence
from datetime import date, datetime, timedelta, tzinfo
from os import PathLike
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Protocol,
    SupportsIndex,
    TYPE_CHECKING,
    Type as type_t,
    TypeVar,
    Union,
    overload,
)
from pandas._libs import NaTType, Period, Timedelta, Timestamp
from pandas._libs.tslibs import BaseOffset
from pandas.core.dtypes.dtypes import ExtensionDtype
from pandas import Interval
from pandas.arrays import DatetimeArray, TimedeltaArray
from pandas.core.arrays.base import ExtensionArray
from pandas.core.frame import DataFrame
from pandas.core.generic import NDFrame
from pandas.core.groupby.generic import DataFrameGroupBy, GroupBy, SeriesGroupBy
from pandas.core.indexes.base import Index
from pandas.core.internals import (
    ArrayManager,
    BlockManager,
    SingleArrayManager,
    SingleBlockManager,
)
from pandas.core.resample import Resampler
from pandas.core.series import Series
from pandas.core.window.rolling import BaseWindow
from pandas.io.formats.format import EngFormatter
from pandas.tseries.holiday import AbstractHolidayCalendar

if TYPE_CHECKING:
    ScalarLike_co = Union[
        int,
        float,
        complex,
        str,
        bytes,
        np.generic,
    ]
    NumpyValueArrayLike = Union[ScalarLike_co, npt.ArrayLike]
    NumpySorter = Optional[npt._ArrayLikeInt_co]
else:
    ...
HashableT = TypeVar("HashableT", bound=Hashable)
MutableMappingT = TypeVar("MutableMappingT", bound=MutableMapping)
ArrayLike = Union["ExtensionArray", np.ndarray]
AnyArrayLike = Union[ArrayLike, "Index", "Series"]
TimeArrayLike = Union["DatetimeArray", "TimedeltaArray"]
_T_co = TypeVar("_T_co", covariant=True)

class SequenceNotStr(Protocol[_T_co]):
    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _T_co: ...
    @overload
    def __getitem__(self, index: slice, /) -> Sequence[_T_co]: ...
    def __contains__(self, value: object, /) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[_T_co]: ...
    def index(self, value: Any, /, start: int = ..., stop: int = ...) -> int: ...
    def count(self, value: Any, /) -> int: ...
    def __reversed__(self) -> Iterator[_T_co]: ...

ListLike = Union[AnyArrayLike, SequenceNotStr, range]
PythonScalar = Union[str, float, bool]
DatetimeLikeScalar = Union["Period", "Timestamp", "Timedelta"]
PandasScalar = Union["Period", "Timestamp", "Timedelta", "Interval"]
Scalar = Union[PythonScalar, PandasScalar, np.datetime64, np.timedelta64, date]
IntStrT = TypeVar("IntStrT", bound=Union[int, str])
TimestampConvertibleTypes = Union[
    "Timestamp", date, np.datetime64, np.int64, float, str
]
TimestampNonexistent = Union[
    Literal["shift_forward", "shift_backward", "NaT", "raise"], timedelta
]
TimedeltaConvertibleTypes = Union[
    "Timedelta", timedelta, np.timedelta64, np.int64, float, str
]
Timezone = Union[str, tzinfo]
ToTimestampHow = Literal["s", "e", "start", "end"]
NDFrameT = TypeVar("NDFrameT", bound="NDFrame")
NumpyIndexT = TypeVar("NumpyIndexT", np.ndarray, "Index")
AxisInt = int
Axis = Union[AxisInt, Literal["index", "columns", "rows"]]
IndexLabel = Union[Hashable, Sequence[Hashable]]
Level = Hashable
Shape = tuple[int, ...]
Suffixes = tuple[Optional[str], Optional[str]]
Ordered = Optional[bool]
JSONSerializable = Optional[Union[PythonScalar, list, dict]]
Frequency = Union[str, "BaseOffset"]
Axes = ListLike
RandomState = Union[
    int,
    np.ndarray,
    np.random.Generator,
    np.random.BitGenerator,
    np.random.RandomState,
]
NpDtype = Union[str, np.dtype, type_t[Union[str, complex, bool, object]]]
Dtype = Union["ExtensionDtype", NpDtype]
AstypeArg = Union["ExtensionDtype", "npt.DTypeLike"]
DtypeArg = Union[Dtype, dict[Hashable, Dtype]]
DtypeObj = Union[np.dtype, "ExtensionDtype"]
ConvertersArg = dict[Hashable, Callable[[Dtype], Dtype]]
ParseDatesArg = Union[
    bool, list[Hashable], list[list[Hashable]], dict[Hashable, list[Hashable]]
]
Renamer = Union[Mapping[Any, Hashable], Callable[[Any], Hashable]]
T = TypeVar("T")
FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)
ValueKeyFunc = Optional[Callable[["Series"], Union["Series", AnyArrayLike]]]
IndexKeyFunc = Optional[Callable[["Index"], Union["Index", AnyArrayLike]]]
AggFuncTypeBase = Union[Callable, str]
AggFuncTypeDict = MutableMapping[
    Hashable, Union[AggFuncTypeBase, list[AggFuncTypeBase]]
]
AggFuncType = Union[
    AggFuncTypeBase,
    list[AggFuncTypeBase],
    AggFuncTypeDict,
]
AggObjType = Union[
    "Series",
    "DataFrame",
    "GroupBy",
    "SeriesGroupBy",
    "DataFrameGroupBy",
    "BaseWindow",
    "Resampler",
]
PythonFuncType = Callable[[Any], Any]
AnyStr_co = TypeVar("AnyStr_co", str, bytes, covariant=True)
AnyStr_contra = TypeVar("AnyStr_contra", str, bytes, contravariant=True)

class BaseBuffer(Protocol):
    @property
    def mode(self) -> str: ...
    def seek(self, __offset: int, __whence: int = ...) -> int: ...
    def seekable(self) -> bool: ...
    def tell(self) -> int: ...

class ReadBuffer(BaseBuffer, Protocol[AnyStr_co]):
    def read(self, __n: int = ...) -> AnyStr_co: ...

class WriteBuffer(BaseBuffer, Protocol[AnyStr_contra]):
    def write(self, __b: AnyStr_contra) -> Any: ...
    def flush(self) -> Any: ...

class ReadPickleBuffer(ReadBuffer[bytes], Protocol):
    def readline(self) -> bytes: ...

class WriteExcelBuffer(WriteBuffer[bytes], Protocol):
    def truncate(self, size: int | None = ...) -> int: ...

class ReadCsvBuffer(ReadBuffer[AnyStr_co], Protocol):
    def __iter__(self) -> Iterator[AnyStr_co]: ...
    def fileno(self) -> int: ...
    def readline(self) -> AnyStr_co: ...
    @property
    def closed(self) -> bool: ...

FilePath = Union[str, "PathLike[str]"]
StorageOptions = Optional[dict[str, Any]]
CompressionDict = dict[str, Any]
CompressionOptions = Optional[
    Union[Literal["infer", "gzip", "bz2", "zip", "xz", "zstd", "tar"], CompressionDict]
]
FormattersType = Union[
    list[Callable], tuple[Callable, ...], Mapping[Union[str, int], Callable]
]
ColspaceType = Mapping[Hashable, Union[str, int]]
FloatFormatType = Union[str, Callable, "EngFormatter"]
ColspaceArgType = Union[
    str, int, Sequence[Union[str, int]], Mapping[Hashable, Union[str, int]]
]
FillnaOptions = Literal["backfill", "bfill", "ffill", "pad"]
InterpolateOptions = Literal[
    "linear",
    "time",
    "index",
    "values",
    "nearest",
    "zero",
    "slinear",
    "quadratic",
    "cubic",
    "barycentric",
    "polynomial",
    "krogh",
    "piecewise_polynomial",
    "spline",
    "pchip",
    "akima",
    "cubicspline",
    "from_derivatives",
]
Manager = Union[
    "ArrayManager", "SingleArrayManager", "BlockManager", "SingleBlockManager"
]
SingleManager = Union["SingleArrayManager", "SingleBlockManager"]
Manager2D = Union["ArrayManager", "BlockManager"]
ScalarIndexer = Union[int, np.integer]
SequenceIndexer = Union[slice, list[int], np.ndarray]
PositionalIndexer = Union[ScalarIndexer, SequenceIndexer]
PositionalIndexerTuple = tuple[PositionalIndexer, PositionalIndexer]
PositionalIndexer2D = Union[PositionalIndexer, PositionalIndexerTuple]
if TYPE_CHECKING:
    TakeIndexer = Union[Sequence[int], Sequence[np.integer], npt.NDArray[np.integer]]
else:
    ...
IgnoreRaise = Literal["ignore", "raise"]
WindowingRankType = Literal["average", "min", "max"]
CSVEngine = Literal["c", "python", "pyarrow", "python-fwf"]
JSONEngine = Literal["ujson", "pyarrow"]
XMLParsers = Literal["lxml", "etree"]
HTMLFlavors = Literal["lxml", "html5lib", "bs4"]
IntervalLeftRight = Literal["left", "right"]
IntervalClosedType = Union[IntervalLeftRight, Literal["both", "neither"]]
DatetimeNaTType = Union[datetime, "NaTType"]
DateTimeErrorChoices = Union[IgnoreRaise, Literal["coerce"]]
SortKind = Literal["quicksort", "mergesort", "heapsort", "stable"]
NaPosition = Literal["first", "last"]
NsmallestNlargestKeep = Literal["first", "last", "all"]
QuantileInterpolation = Literal["linear", "lower", "higher", "midpoint", "nearest"]
PlottingOrientation = Literal["horizontal", "vertical"]
AnyAll = Literal["any", "all"]
MergeHow = Literal["left", "right", "inner", "outer", "cross"]
MergeValidate = Literal[
    "one_to_one",
    "1:1",
    "one_to_many",
    "1:m",
    "many_to_one",
    "m:1",
    "many_to_many",
    "m:m",
]
JoinHow = Literal["left", "right", "inner", "outer"]
JoinValidate = Literal[
    "one_to_one",
    "1:1",
    "one_to_many",
    "1:m",
    "many_to_one",
    "m:1",
    "many_to_many",
    "m:m",
]
ReindexMethod = Union[FillnaOptions, Literal["nearest"]]
MatplotlibColor = Union[str, Sequence[float]]
TimeGrouperOrigin = Union[
    "Timestamp", Literal["epoch", "start", "start_day", "end", "end_day"]
]
TimeAmbiguous = Union[Literal["infer", "NaT", "raise"], "npt.NDArray[np.bool_]"]
TimeNonexistent = Union[
    Literal["shift_forward", "shift_backward", "NaT", "raise"], timedelta
]
DropKeep = Literal["first", "last", False]
CorrelationMethod = Union[
    Literal["pearson", "kendall", "spearman"], Callable[[np.ndarray, np.ndarray], float]
]
AlignJoin = Literal["outer", "inner", "left", "right"]
DtypeBackend = Literal["pyarrow", "numpy_nullable"]
TimeUnit = Literal["s", "ms", "us", "ns"]
OpenFileErrors = Literal[
    "strict",
    "ignore",
    "replace",
    "surrogateescape",
    "xmlcharrefreplace",
    "backslashreplace",
    "namereplace",
]
UpdateJoin = Literal["left"]
NaAction = Literal["ignore"]
FromDictOrient = Literal["columns", "index", "tight"]
ToGbqIfexist = Literal["fail", "replace", "append"]
ToStataByteorder = Literal[">", "<", "little", "big"]
ExcelWriterIfSheetExists = Literal["error", "new", "replace", "overlay"]
OffsetCalendar = Union[np.busdaycalendar, "AbstractHolidayCalendar"]
UsecolsArgType = Union[
    SequenceNotStr[Hashable],
    range,
    AnyArrayLike,
    Callable[[HashableT], bool],
    None,
]
