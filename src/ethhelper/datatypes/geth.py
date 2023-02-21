import typing
from typing import Any

import orjson
from eth_typing import ChecksumAddress
from pydantic import BaseModel, Field
from web3.types import CallOverrideParams as Web3CallOverrideParams
from web3.types import Nonce

from ..utils import json
from ..utils.stdtype import HexBytes
from .base import Wei


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
    id: int | None = None
    result: Any

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethErrorDetail(BaseModel):
    code: int
    message: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethErrorResponse(BaseModel):
    id: int | None
    error: GethErrorDetail

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

    def to_hex(self) -> Any:
        td = self.dict(by_alias=True, exclude_none=True)
        if "balance" in td:
            td["balance"] = "0x" + \
                typing.cast(Wei, td["balance"]).value.to_bytes(
                    32, "big", signed=False
                ).hex()
        if "nonce" in td:
            td["nonce"] = typing.cast(Nonce, td["nonce"]).to_bytes(
                8, "big", signed=False
            ).hex()
        if "code" in td:
            td["code"] = typing.cast(HexBytes, td["code"]).to_str()

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
