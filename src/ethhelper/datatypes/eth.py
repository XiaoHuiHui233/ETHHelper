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
    """An entry representing an address with associated storage keys in an
    access list.
    """
    address: Address
    """The address of the entry."""
    storage_keys: list[Hash32] = Field(alias="storageKeys")
    """The storage keys associated with the entry."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


AccessList = NewType("AccessList", Sequence[AccessEntry])
"""A new type representing a sequence of ``AccessEntry`` instances."""


class SyncStatus(BaseModel):
    """The current synchronization status of the Ethereum node."""
    current_block: int = Field(alias="currentBlock")
    """The current block number."""
    highest_block: int = Field(alias="highestBlock")
    """The highest block number seen."""
    starting_block: int = Field(alias="startingBlock")
    """The block number at which the node started syncing."""

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class FeeHistory(BaseModel):
    """A record of base fees and gas usage ratios."""
    base_fee_per_gas: list[Wei] = Field(alias="baseFeePerGas")
    """A list of base fees per gas for each block in the history."""
    gas_used_ratio: list[float] = Field(alias="gasUsedRatio")
    """A list of gas used ratios for each block in the history."""
    oldest_block: BlockNumber = Field(alias="oldestBlock")
    """The block number of the oldest block in the history."""
    reward: list[list[Wei]] | None
    """A nested list of miner rewards for each block in the history, or
    ``None`` if rewards are not available.
    """

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


class TxParams(BaseModel):
    """Represents a set of parameters required for creating a transaction."""
    chain_id: int | None = Field(None, alias="chainId")
    """The chain ID for the transaction."""
    data: HexBytes | None = None
    """The data payload of the transaction."""
    from_: Address | ENS | None = Field(None, alias="from")
    """The sender's address or ENS name."""
    gas: Gas | None = None
    """The maximum amount of gas to use for the transaction."""
    # legacy pricing
    gas_price: Wei | None = Field(None, alias="gasPrice")
    """The price of gas for the transaction. (Legacy pricing)"""
    # dynamic fee pricing
    max_fee_per_gas: Wei | None = Field(None, alias="maxFeePerGas")
    """The maximum fee per gas for the transaction. (Dynamic fee pricing)"""
    max_priority_fee_per_gas: Wei | None = \
        Field(None, alias="maxPriorityFeePerGas")
    """The maximum priority fee per gas for the transaction. (Dynamic fee
    pricing)
    """
    nonce: Nonce | None = None
    """A unique number used to prevent replay attacks."""
    # addr or ens
    to: Address | ENS
    """The recipient's address or ENS name."""
    type: int | None = None
    """The transaction type, if the chain supports EIP-2718."""
    value: Wei | None = None
    """The amount of Ether to send along with the transaction."""

    def to_web3(self) -> Web3TxParams:
        """Convert the transaction parameters to ``web3.types.TxParams``
        format.

        Returns:
            A dictionary representing the transaction parameters in
            ``web3.types.TxParams`` format.
        """

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
    """A class representing an Ethereum transaction."""
    chain_id: int = Field(1, alias="chainId")
    """The chain ID for the transaction."""
    block_hash: Hash32 | None = Field(alias="blockHash")
    """The hash of the block containing the transaction."""
    block_number: BlockNumber | None = Field(alias="blockNumber")
    """The block number containing the transaction."""
    transaction_index: int | None = Field(alias="transactionIndex")
    """The transaction index within the block."""
    hash: Hash32
    """The hash of the transaction."""
    from_: Address = Field(alias="from")
    """The address of the sender of the transaction."""
    to: Address | None
    """The address of the recipient of the transaction (if applicable)."""
    gas: Gas
    """The gas limit for the transaction."""
    gas_price: Wei = Field(alias="gasPrice")
    """The gas price for the transaction."""
    max_fee_per_gas: Wei | None = Field(None, alias="maxFeePerGas")
    """The maximum fee per gas for the transaction (if applicable)."""
    max_priority_fee_per_gas: Wei | None = Field(
        None, alias="maxPriorityFeePerGas"
    )
    """The maximum priority fee per gas for the transaction (if applicable)."""
    input: HexBytes
    """The input data for the transaction."""
    value: Wei
    """The value of the transaction in Wei."""
    nonce: Nonce
    """The nonce of the transaction."""
    type: int
    """The type of the transaction (0 for legacy, 1 for EIP-2930, 2 for
    EIP-1559).
    """
    access_list: AccessList | None = Field(None, alias="accessList")
    """The access list for the transaction (if applicable)."""
    r: HexBytes
    """The r value of the transaction signature."""
    s: HexBytes
    """The s value of the transaction signature."""
    v: int
    """The v value of the transaction signature."""
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
    """The difficulty (in hashes) of mining this block. After the Merge
    (15537394), this value will be always 0.
    """
    extra_data: HexBytes = Field(alias="extraData")
    """Additional data provided by the miner. After the Merge (15537394), this
    value will be always empty bytes.
    """
    gas_limit: Gas = Field(alias="gasLimit")
    """The maximum amount of gas that was available to transactions in this
        block.
    """
    gas_used: Gas = Field(alias="gasUsed")
    """The amount of gas that was used to execute transactions in this block.
    """
    base_fee_per_gas: Wei | None = Field(None, alias="baseFeePerGas")
    """The fee per unit of gas burned by the protocol in this block. Before
        EIP-1559 (12965000), this value was always None.
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
        the Merge (15537394), this value will be the beacon chain's RANDAO
        value.
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
    """A list of hash of the uncle blocks of this block. After the Merge
    (15537394), this value will be always None.
    """
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
    """The number of the block in which the log was generated."""
    block_hash: Hash32 = Field(alias="blockHash")
    """The hash of the block in which the log was generated."""
    log_index: int = Field(alias="logIndex")
    """The index of this log in the block."""
    address: Address
    """The address of the contract that generated this log."""
    topics: list[Hash32]
    """A list of up to 4 32-byte indexed topics for the log."""
    data: HexBytes
    """The unindexed data for this log."""
    transaction_hash: Hash32 = Field(alias="transactionHash")
    """The hash (32 bytes) of the transaction that generated this log."""
    transaction_index: int = Field(alias="transactionIndex")
    """The index of the transaction in the block."""
    removed: bool
    """Whether or not the log was removed from the blockchain."""
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
    """A transaction receipt."""
    block_number: BlockNumber = Field(alias="blockNumber")
    """The number of the block this receipt is associated with."""
    block_hash: Hash32 = Field(alias="blockHash")
    """The hash of the block this receipt is associated with."""
    contract_address: Address | None = Field(alias="contractAddress")
    """The address of the contract created by this transaction if it is a
    contract creation transaction, otherwise None.
    """
    cumulative_gas_used: Gas = Field(alias="cumulativeGasUsed")
    """The total amount of gas used in the block up to and including this
    transaction.
    """
    effective_gas_price: Wei = Field(alias="effectiveGasPrice")
    """The amount of ETH paid per unit of gas in the transaction, including the
    amount that is burned by EIP-1559.
    """
    from_: Address = Field(alias="from")
    """The address of the account that sent this transaction."""
    gas_used: Gas = Field(alias="gasUsed")
    """The amount of gas used by this transaction."""
    logs: list[Log]
    """The logs emitted by this transaction."""
    logs_bloom: HexBytes = Field(alias="logsBloom")
    """A bloom filter of the logs emitted by this transaction."""
    status: int
    """The status code of this transaction, where 0 represents success and
    non-zero represents failure."""
    to: Address
    """The address of the account or contract that received this transaction.
    """
    transaction_hash: Hash32 = Field(alias="transactionHash")
    """The hash of the transaction that generated this receipt."""
    transaction_index: int = Field(alias="transactionIndex")
    """The index of this transaction in the block."""
    type: int
    """The type of this transaction, where 0 represents a legacy transaction,
    1 represents an EIP-2930 transaction, and 2 represents an EIP-1559
    transaction.
    """
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
    """Parameters used for creating Ethereum filters."""
    address: Address | list[Address] | None = None
    """An Ethereum address or list of addresses to filter on. If None, all
        addresses are filtered.
    """
    block_hash: Hash32 | None = Field(None, alias="blockHash")
    """A block hash (32 bytes) to filter on. If None, all blocks are filtered.
    """
    from_block: BlockIdentifier | None = Field(None, alias="fromBlock")
    """The starting block for filtering. If None, the filter will start from
        the earliest block.
    """
    to_block: BlockIdentifier | None = Field(None, alias="toBlock")
    """The ending block for filtering. If None, the filter will end at the
        latest block.
    """
    topics: Sequence[Hash32 | Sequence[Hash32]] | None = None
    """A list of topics (32 bytes) to filter on. Each topic can be a single
        value or a list of values. If None, all topics are filtered.
    """

    def to_web3(self) -> Web3FilterParams:
        """Converts the ``FilterParams`` object to a
        ``web3.types.FilterParams`` object.
        """
        td = self.dict(by_alias=True, exclude_none=True)
        if "address" in td:
            if isinstance(td["address"], Address):
                td["address"] = td["address"].to_web3()
            else:
                td["address"] = typing.cast(list[Address], td["address"])
                td["address"] = [addr.to_web3() for addr in td["address"]]
        if "blockHash" in td:
            td["blockHash"] = str(typing.cast(Hash32, td["blockHash"]))
            if "fromBlock" in td or "toBlock" in td:
                raise ValueError(
                    "You should only choose one of blockHash or "
                    "fromBlock/toBlock as filter params"
                )
        if "fromBlock" in td:
            td["fromBlock"] = convert.block_id_transfer(td["fromBlock"])
            if "toBlock" not in td:
                td["toBlock"] = "latest"
        if "toBlock" in td:
            td["toBlock"] = convert.block_id_transfer(td["toBlock"])
            if "fromBlock" not in td:
                td["fromBlock"] = "latest"
        if "topics" in td and len(td["topics"]) != 0:
            td["topics"] = typing.cast(
                Sequence[Hash32 | Sequence[Hash32]], td["topics"]
            )
            if isinstance(td["topics"][0], Sequence):
                td["topics"] = typing.cast(
                    Sequence[Sequence[Hash32]], td["topics"]
                )
                td["topics"] = [
                    [str(top2) for top2 in top1] for top1 in td["topics"]
                ]
            else:
                td["topics"] = typing.cast(Sequence[Hash32], td["topics"])
                td["topics"] = [str(top) for top in td["topics"]]
        return typing.cast(Web3FilterParams, td)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps
