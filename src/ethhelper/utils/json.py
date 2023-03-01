from typing import Any, TypeVar

import orjson

from ethhelper.datatypes.base import HexBytes, IntStr

T = TypeVar("T", IntStr, HexBytes)


def encode_my_class(v: Any) -> Any:
    if isinstance(v, IntStr):
        return v.to_int_or_str()
    elif isinstance(v, HexBytes):
        return str(v)
    raise TypeError


def orjson_dumps(v: Any, **kwargs: Any) -> str:
    return orjson.dumps(
        v, default=encode_my_class, option=orjson.OPT_NON_STR_KEYS
    ).decode()
