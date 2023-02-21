from typing import NewType, Sequence

import orjson
from eth_typing import Address as Web3Address
from eth_typing import BlockNumber
from eth_typing import Hash32 as EthHash32
from pydantic import BaseModel, Field
from web3.types import BlockParams
from web3.types import Wei as Web3Wei

from ..utils import json
from ..utils.stdtype import HexBytes, IntStr


class Hash32(HexBytes):
    def to_web3(self) -> EthHash32:
        return EthHash32(self.value)


class Address(HexBytes):
    def to_web3(self) -> Web3Address:
        return Web3Address(self.value)


BlockIdentifier = BlockParams | BlockNumber | Hash32
Gas = NewType("Gas", int)


class Wei(IntStr):
    def to_web3(self) -> Web3Wei:
        return Web3Wei(self.value)


class AccessEntry(BaseModel):
    address: Address
    storage_keys: list[Hash32] = Field(alias="storageKeys")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


AccessList = NewType("AccessList", Sequence[AccessEntry])
