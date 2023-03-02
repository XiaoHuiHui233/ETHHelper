import typing
from typing import (
    NewType,
    Sequence,
)

from eth_typing import (
    BlockNumber,
)
import orjson
from pydantic import (
    BaseModel,
    Field,
)
from web3.types import (
    ENS,
    FilterParams as Web3FilterParams,
    Nonce,
    TxParams as Web3TxParams,
)

from ethhelper.utils import (
    convert,
    json,
)

from .base import (
    Address,
    BlockIdentifier,
    Gas,
    Hash32,
    HexBytes,
    IntStr,
    Wei,
)


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


class SyncStatus(BaseModel):
    current_block: int = Field(alias="currentBlock")
    highest_block: int = Field(alias="highestBlock")
    known_states: int = Field(alias="knownStates")
    pulled_states: int = Field(alias="pulledStates")
    starting_block: int = Field(alias="startingBlock")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class FeeHistory(BaseModel):
    base_fee_per_gas: list[Wei] = Field(alias="baseFeePerGas")
    gas_used_ratio: list[float] = Field(alias="gasUsedRatio")
    oldest_block: BlockNumber = Field(alias="oldestBlock")
    reward: list[list[Wei]] | None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxParams(BaseModel):
    chain_id: int | None = Field(None, alias="chainId")
    data: HexBytes | None = None
    from_: Address | ENS | None = Field(None, alias="from")
    gas: Gas | None = None
    # legacy pricing
    gas_price: Wei | None = Field(None, alias="gasPrice")
    # dynamic fee pricing
    max_fee_per_gas: Wei | None = Field(None, alias="maxFeePerGas")
    max_priority_fee_per_gas: Wei | None = \
        Field(None, alias="maxPriorityFeePerGas")
    nonce: Nonce | None = None
    # addr or ens
    to: Address | ENS
    type: int | None = None
    value: Wei | None = None

    def to_web3(self) -> Web3TxParams:
        td = self.dict(by_alias=True, exclude_none=True)
        if isinstance(td["to"], Address):
            td["to"] = td["to"].to_web3()
        if "data" in td:
            td["data"] = typing.cast(HexBytes, td["data"]).value
        if "from" in td:
            if isinstance(td["from"], Address):
                td["from"] = td["from"].to_web3()
        if "gasPrice" in td:
            td["gasPrice"] = typing.cast(Wei, td["gasPrice"]).to_web3()
        if "maxFeePerGas" in td:
            td["maxFeePerGas"] = typing.cast(Wei, td["maxFeePerGas"]).to_web3()
        if "maxPriorityFeePerGas" in td:
            td["maxPriorityFeePerGas"] = \
                typing.cast(Wei, td["maxPriorityFeePerGas"]).to_web3()
        if "value" in td:
            td["value"] = typing.cast(Wei, td["value"]).to_web3()
        return typing.cast(Web3TxParams, td)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class Transaction(BaseModel):
    chain_id: int = Field(1, alias="chainId")
    block_hash: Hash32 | None = Field(alias="blockHash")
    block_number: BlockNumber | None = Field(alias="blockNumber")
    transaction_index: int | None = Field(alias="transactionIndex")
    hash: Hash32
    from_: Address = Field(alias="from")
    to: Address | None
    gas: Gas
    gas_price: Wei = Field(alias="gasPrice")
    max_fee_per_gas: Wei | None = Field(None, alias="maxFeePerGas")
    max_priority_fee_per_gas: Wei | None = Field(
        None, alias="maxPriorityFeePerGas"
    )
    input: HexBytes
    value: Wei
    nonce: Nonce
    type: int
    access_list: AccessList | None = Field(None, alias="accessList")
    r: HexBytes
    s: HexBytes
    v: int
    # vaildators
    int_val = convert.int_validator(
        "block_number", "gas", "gas_price", "max_fee_per_gas", "v",
        "max_priority_fee_per_gas", "nonce", "value", "type", "chain_id"
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class Block(BaseModel):
    difficulty: IntStr
    """A measure of the difficulty of mining this block. After the Merge
        (15537394), this value is always 0.
    """
    extra_data: HexBytes = Field(alias="extraData")
    """An arbitrary data field supplied by the miner. After the Merge
        (15537394), this value is always empty bytes.
    """
    gas_limit: Gas = Field(alias="gasLimit")
    """The maximum amount of gas that was available to transactions in this
        block.
    """
    gas_used: Gas = Field(alias="gasUsed")
    """The amount of gas that was used executing transactions in this block."""
    base_fee_per_gas: Wei | None = Field(None, alias="baseFeePerGas")
    """The fee per unit of gas burned by the protocol in this block. Before
        EIP-1559 (12965000), this value is always None.
    """
    logs_bloom: HexBytes = Field(alias="logsBloom")
    """A bloom filter that can be used to check if a block may contain log
        entries matching a filter.
    """
    miner: Address
    """The address (20 bytes) of the account that mined this block."""
    nonce: HexBytes
    """The block nonce, a sequence (8 bytes) determined by the miner."""
    number: BlockNumber
    """The number of this block, starting at 0 for the genesis block."""
    parent_hash: Hash32 = Field(alias="parentHash")
    """The hash (32 bytes) of the parent block of this block."""
    hash: Hash32
    """The hash (32 bytes) of this block."""
    mix_hash: Hash32 = Field(alias="mixHash")
    """The hash (32 bytes) that was used as an input to the PoW process. After
        the Merge (15537394), this value is the beacon chain's RANDAO value.
    """
    receipts_root: HexBytes = Field(alias="receiptsRoot")
    """The keccak256 hash (32 bytes) of the trie of transaction receipts in
        this block.
    """
    sha3_uncles: HexBytes = Field(alias="sha3Uncles")
    """The keccak256 hash (32 bytes) of all the ommers (AKA uncles) associated
        with this block.
    """
    state_root: HexBytes = Field(alias="stateRoot")
    """The keccak256 hash (32 bytes) of the state trie after this block was
        processed.
    """
    timestamp: int
    """The unix timestamp at which this block was mined."""
    transactions_root: HexBytes = Field(alias="transactionsRoot")
    """The keccak256 hash (32 bytes) of the root of the trie of transactions in
        this block.
    """
    size: int | None = None
    """The block size in bytes"""
    total_difficulty: IntStr | None = Field(None, alias="totalDifficulty")
    """The sum of all difficulty values up to and including this block. After
        the Merge (15537394), this value is always 58750003716598352816469.
    """
    transactions: list[Hash32] | list[Transaction] | None = None
    """A list of the hash (32 bytes) of transactions associated with this
        block.
    """
    uncles: list[Hash32] | None = None
    # vaildators
    int_val = convert.int_validator(
        "difficulty", "gas_limit", "gas_used", "base_fee_per_gas", "number",
        "timestamp", "size", "total_difficulty"
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class Log(BaseModel):
    """A published Ethereum event log."""
    block_number: BlockNumber = Field(alias="blockNumber")
    block_hash: Hash32 = Field(alias="blockHash")
    log_index: int = Field(alias="logIndex")
    """The index of this log in the block."""
    address: Address
    """The address (20 bytes) of the account which generated this log - this
        will always be a contract account.
    """
    topics: list[Hash32]
    """A list of 0-4 indexed topics (32 bytes) for the log."""
    data: HexBytes
    """Unindexed data for this log."""
    transaction_hash: Hash32 = Field(alias="transactionHash")
    """The hash (32 bytes) of the transaction that generated this log entry."""
    transaction_index: int = Field(alias="transactionIndex")
    removed: bool
    # vaildators
    int_val = convert.int_validator(
        "block_number", "log_index", "transaction_index"
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class Receipt(BaseModel):
    block_number: BlockNumber = Field(alias="blockNumber")
    block_hash: Hash32 = Field(alias="blockHash")
    contract_address: Address | None = Field(alias="contractAddress")
    cumulative_gas_used: Gas = Field(alias="cumulativeGasUsed")
    effective_gas_price: Wei = Field(alias="effectiveGasPrice")
    from_: Address = Field(alias="from")
    gas_used: Gas = Field(alias="gasUsed")
    logs: list[Log]
    logs_bloom: HexBytes = Field(alias="logsBloom")
    status: int
    to: Address
    transaction_hash: Hash32 = Field(alias="transactionHash")
    transaction_index: int = Field(alias="transactionIndex")
    type: int
    # vaildators
    int_val = convert.int_validator(
        "block_number", "cumulative_gas_used", "effective_gas_price",
        "gas_used", "status", "transaction_index", "type"
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class FilterParams(BaseModel):
    address: Address | list[Address] | None = None
    block_hash: HexBytes | None = Field(None, alias="blockHash")
    from_block: BlockIdentifier = Field("latest", alias="fromBlock")
    to_block: BlockIdentifier = Field("latest", alias="toBlock")
    topics: Sequence[Hash32 | Sequence[Hash32]] | None = None

    def to_web3(self) -> Web3FilterParams:
        td = self.dict(by_alias=True, exclude_none=True)
        if "address" in td:
            if isinstance(td["address"], Address):
                td["address"] = td["address"].to_web3()
            else:
                td["address"] = typing.cast(list[Address], td["address"])
                td["address"] = [addr.to_web3() for addr in td["address"]]
        if "blockHash" in td:
            td["blockHash"] = typing.cast(HexBytes, td["blockHash"]).value
        if "fromBlock" in td:
            td["fromBlock"] = convert.block_id_transfer(td["fromBlock"])
        if "toBlock" in td:
            td["toBlock"] = convert.block_id_transfer(td["toBlock"])
        if "topics" in td and len(td["topics"]) != 0:
            td["topics"] = typing.cast(
                Sequence[Hash32 | Sequence[Hash32]], td["topics"]
            )
            if isinstance(td["topics"][0], Sequence):
                td["topics"] = typing.cast(
                    Sequence[Sequence[Hash32]], td["topics"]
                )
                td["topics"] = [
                    [top2.to_web3() for top2 in top1] for top1 in td["topics"]
                ]
            else:
                td["topics"] = typing.cast(Sequence[Hash32], td["topics"])
                td["topics"] = [top.to_web3() for top in td["topics"]]
        return typing.cast(Web3FilterParams, td)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps
