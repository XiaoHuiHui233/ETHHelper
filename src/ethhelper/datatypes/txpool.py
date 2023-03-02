from typing import (
    Any,
)

from eth_typing import (
    ChecksumAddress,
)
import orjson
from pydantic import (
    BaseModel,
)
from web3.types import (
    Nonce,
)

from ethhelper.utils import (
    convert,
    json,
)

from .base import (
    Address,
    Gas,
    Wei,
)
from .eth import (
    Transaction,
)


class TxpoolStatus(BaseModel):
    pending: int
    queued: int
    # vaildators
    int_val = convert.int_validator("pending", "queued")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolSnapshot(BaseModel):
    contract_creation: bool = False
    to_address: Address
    fee: Wei
    gas: Gas
    gas_fee: Wei
    # vaildators
    int_val = convert.int_validator("fee", "gas", "gas_fee")

    @classmethod
    def validate(cls, value: Any) -> "TxpoolSnapshot":
        if not isinstance(value, str):
            return super(TxpoolSnapshot, cls).validate(value)
        ss = value.split(": ")
        contract_creation = ss[0] == "contract creation"
        if contract_creation:
            ss[0] = "0x0000000000000000000000000000000000000000"
        to_address = Address(ss[0])
        ss = ss[1].split(" + ")
        fee = Wei(ss[0][:-4])
        ss = ss[1].split(" × ")
        gas = Gas(int(ss[0][:-4]))
        gas_fee = Wei(ss[1][:-4])
        return cls(
            contract_creation=contract_creation,
            to_address=to_address,
            fee=fee,
            gas=gas,
            gas_fee=gas_fee
        )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolInspect(BaseModel):
    pending: dict[ChecksumAddress, dict[Nonce, TxpoolSnapshot]]
    queued: dict[ChecksumAddress, dict[Nonce, TxpoolSnapshot]]

    class Config:
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolContent(BaseModel):
    pending: dict[ChecksumAddress, dict[Nonce, Transaction]]
    queued: dict[ChecksumAddress, dict[Nonce, Transaction]]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolContentFrom(BaseModel):
    pending: dict[Nonce, Transaction]
    queued: dict[Nonce, Transaction]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps
