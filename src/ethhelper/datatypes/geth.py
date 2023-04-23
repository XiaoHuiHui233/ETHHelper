import typing
from typing import (
    Any,
)

from eth_typing import (
    ChecksumAddress,
)
import orjson
from pydantic import (
    BaseModel,
    Field,
    validator,
)
from web3.types import (
    CallOverrideParams as Web3CallOverrideParams,
    Nonce,
)

from ethhelper.utils import (
    json,
)

from .base import (
    HexBytes,
    Wei,
)


class IdNotMatch(Exception):
    """An exception raised when a JSON-RPC response ID doesn't match the
    request ID.
    """
    pass


class GethIsDead(Exception):
    """An exception raised when the Geth client is not running."""
    pass


class NoSubscribeToken(Exception):
    """An exception raised when attempting to subscribe to an Ethereum event
    without a subscription token.
    """
    pass


class GethRequest(BaseModel):
    """A class representing a JSON-RPC request to the Geth client."""
    jsonrpc: str = "2.0"
    """The version of the JSON-RPC protocol."""
    id: int | None = None
    """The ID of the request, or None if it is a notification."""
    method: str
    """The name of the RPC method to call."""
    params: list[Any]
    """A list of parameters to pass to the RPC method."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethSuccessResponse(BaseModel):
    """A class representing a successful JSON-RPC response from the Geth
    client.
    """
    jsonrpc: str = "2.0"
    """The version of the JSON-RPC protocol."""
    id: int | None = None
    """The ID of the response, or None if it is a notification."""
    result: Any
    """The result of the RPC method call."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethErrorDetail(BaseModel):
    """A class representing the error details in a JSON-RPC error response from
    the Geth client.
    """
    jsonrpc: str = "2.0"
    """The version of the JSON-RPC protocol."""
    code: int
    """The error code."""
    message: str
    """A description of the error."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethError(Exception):
    """An exception representing an error response from the Geth client."""
    def __init__(self, error: GethErrorDetail | list[GethErrorDetail]) -> None:
        if isinstance(error, list):
            super().__init__([f"{err.code}: {err.message}" for err in error])
        else:
            self.code = error.code
            """The error code."""
            self.msg = error.message
            """A description of the error."""
            super().__init__(f"{error.code}: {error.message}")


class GethErrorResponse(BaseModel):
    """A class representing an error response from the Geth client."""
    jsonrpc: str = "2.0"
    """The version of the JSON-RPC protocol."""
    id: int | None
    """The ID of the response, or None if it is a notification."""
    error: GethErrorDetail
    """The details of the error."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


GethResponse = GethSuccessResponse | GethErrorResponse
"""A union class that represents the response data returned by a Geth node.

This class is a union of two other classes: ``GethSuccessResponse`` and
``GethErrorResponse``. Instances of ``GethSuccessResponse`` are returned when
a Geth request is successful, while instances of ``GethErrorResponse`` are
returned when a Geth request fails.
"""


class GethWSItem(BaseModel):
    """A class representing an item in a WebSocket response from the Geth
    client.
    """
    subscription: str
    """The subscription ID."""
    result: Any
    """The result of the subscription."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class GethWSResponse(BaseModel):
    """A class representing a WebSocket response from the Geth client."""
    jsonrpc: str = "2.0"
    """The version of the JSON-RPC protocol."""
    method: str
    """The name of the WebSocket method."""
    params: GethWSItem
    """The item contained in the response."""

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
    """A class representing override parameters for a contract function call.
    """
    balance: Wei | None = None
    """The balance of the caller."""
    nonce: Nonce | None = None
    """The nonce of the caller."""
    code: HexBytes | None = None
    """The code of the contract."""
    state: dict[str, Any] | None = None
    """The current state of the contract."""
    state_diff: dict[ChecksumAddress, dict[str, Any]] | None = \
        Field(None, alias="stateDiff")
    """The difference in the contract state."""

    def to_web3(self) -> Web3CallOverrideParams:
        """Converts the ``CallOverrideParams`` instance to an instance of
        ``web3.types.CallOverrideParams``.

        Returns:
            The converted ``web3.types.CallOverrideParams`` instance.
        """
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
"""A dictionary that maps Ethereum addresses to ``CallOverrideParams``
instances.

This class is used to specify the call override parameters for a smart
contract function. The keys of the dictionary are Ethereum addresses,
and the values are instances of the ``CallOverrideParams`` class, which
specify the call override parameters for the corresponding address.
"""