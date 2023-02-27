import typing
from typing import Any

import orjson
from eth_typing import ChecksumAddress
from pydantic import BaseModel, Field, validator
from web3.types import CallOverrideParams as Web3CallOverrideParams
from web3.types import Nonce

from ..utils import json
from ..utils.stdtype import HexBytes
from .base import Wei


class IdNotMatch(Exception):
    pass


class NoSubscribeToken(Exception):
    pass


class GethRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int | None = None
    method: str
    params: list[Any]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethSuccessResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int | None = None
    result: Any

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethErrorDetail(BaseModel):
    jsonrpc: str = "2.0"
    code: int
    message: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethError(Exception):
    def __init__(self, error: GethErrorDetail) -> None:
        self.code = error.code
        self.msg = error.message
        super().__init__(f"{error.code}: {error.message}")


class GethErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int | None
    error: GethErrorDetail

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethWSItem(BaseModel):
    subscription: str
    result: Any

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethWSResponse(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: GethWSItem

    @validator("params")
    def valid_params(cls, v: Any, **kwargs: Any) -> Any:
        if isinstance(v, str):
            if v != "eth_subscription":
                raise ValueError("Wrong WSResponse")
        return v

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class CallOverrideParams(BaseModel):
    balance: Wei | None = None
    nonce: Nonce | None = None
    code: HexBytes | None = None
    state: dict[str, Any] | None = None
    state_diff: dict[ChecksumAddress, dict[str, Any]] | None = \
        Field(None, alias="stateDiff")

    def to_web3(self) -> Web3CallOverrideParams:
        td = self.dict(by_alias=True, exclude_none=True)
        if "balance" in td:
            td["balance"] = typing.cast(Wei, td["balance"]).to_web3()
        if "code" in td:
            td["code"] = typing.cast(HexBytes, td["code"]).value
        return typing.cast(Web3CallOverrideParams, td)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


CallOverride = dict[ChecksumAddress, CallOverrideParams]
