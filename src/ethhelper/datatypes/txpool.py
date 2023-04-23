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
    """A class that represents the status of transactions in the Ethereum
    transaction pool.
    """
    pending: int
    """The number of pending transactions in the pool."""
    queued: int
    """The number of queued transactions in the pool."""
    # vaildators
    int_val = convert.int_validator("pending", "queued")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolSnapshot(BaseModel):
    """A class that represents a snapshot of the Ethereum transaction pool.
    """

    contract_creation: bool = False
    """Whether the transaction is a contract creation. Defaults to ``False``.
    """
    to_address: Address
    """The address of the recipient of the transaction."""
    fee: Wei
    """The transaction fee in wei."""
    gas: Gas
    """The amount of gas used by the transaction."""
    gas_fee: Wei
    """The gas fee for the transaction in wei."""
    # vaildators
    int_val = convert.int_validator("fee", "gas", "gas_fee")

    @classmethod
    def validate(cls, value: Any) -> "TxpoolSnapshot":
        """Validates the given value and creates a new instance of the
        ``TxpoolSnapshot`` class.

        Args:
            value: The value to be validated and converted.

        Returns:
            The converted ``TxpoolSnapshot`` instance.

        """
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
    """A class that represents the contents of the Ethereum transaction pool.
    """
    pending: dict[ChecksumAddress, dict[Nonce, TxpoolSnapshot]]
    """A dictionary that maps from account address to nonce to snapshot of the
    corresponding transaction in the pending pool.
    """
    queued: dict[ChecksumAddress, dict[Nonce, TxpoolSnapshot]]
    """A dictionary that maps from account address to nonce to snapshot of the
    corresponding transaction in the queued pool."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolContent(BaseModel):
    """A class representing the content of the transaction pool on a node.
    """
    pending: dict[ChecksumAddress, dict[Nonce, Transaction]]
    """A dictionary containing information about all pending transactions in
    the pool.
    
    The keys are the transaction sender's address and the values are
    another dictionary, where the keys are the nonces of the transactions and
    the values are the corresponding transactions.
    """
    queued: dict[ChecksumAddress, dict[Nonce, Transaction]]
    """A dictionary containing information about all queued transactions in the
    pool.
    
    The keys are the transaction sender's address and the values are
    another dictionary, where the keys are the nonces of the transactions and
    the values are the corresponding transactions.
    """

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxpoolContentFrom(BaseModel):
    """A class that represents the transactions in the transaction pool
    (txpool) from a specific address.
    """
    pending: dict[Nonce, Transaction]
    """A dictionary of pending transactions from the specified address. The
    dictionary is indexed by the nonce of each transaction."""
    queued: dict[Nonce, Transaction]
    """A dictionary of queued transactions from the specified address. The
    dictionary is indexed by the nonce of each transaction."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps
