"""
This type stub file was generated by pyright.
"""

from typing import TYPE_CHECKING
from pandas._libs import parsers
from pandas.io.parsers.base_parser import ParserBase
from collections.abc import Hashable, Mapping, Sequence
from pandas._typing import ArrayLike, DtypeArg, DtypeObj, ReadCsvBuffer
from pandas import Index, MultiIndex

if TYPE_CHECKING:
    ...

class CParserWrapper(ParserBase):
    low_memory: bool
    _reader: parsers.TextReader
    def __init__(self, src: ReadCsvBuffer[str], **kwds) -> None: ...
    def close(self) -> None: ...
    def read(self, nrows: int | None = ...) -> tuple[
        Index | MultiIndex | None,
        Sequence[Hashable] | MultiIndex,
        Mapping[Hashable, ArrayLike],
    ]: ...

def ensure_dtype_objs(
    dtype: DtypeArg | dict[Hashable, DtypeArg] | None,
) -> DtypeObj | dict[Hashable, DtypeObj] | None:
    """
    Ensure we have either None, a dtype object, or a dictionary mapping to
    dtype objects.
    """
    ...
