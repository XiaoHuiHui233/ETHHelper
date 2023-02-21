from typing import Any

from pydantic import validator

Validator = Any


def parse_hex_or_strint(v: Any) -> Any:
    if not isinstance(v, str):
        return v
    return int(v, 0)


def int_validator(*fields: str) -> Validator:
    return validator(*fields, pre=True, allow_reuse=True)(
        parse_hex_or_strint
    )
