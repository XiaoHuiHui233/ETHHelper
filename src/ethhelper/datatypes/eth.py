import typing

import orjson
from eth_typing import BlockNumber
from pydantic import BaseModel, Field
from web3.types import ENS, Nonce
from web3.types import TxParams as Web3TxParams

from ..utils import convert, json
from ..utils.stdtype import HexBytes, IntStr
from .base import AccessList, Address, Gas, Hash32, Wei


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

    # @root_validator()
    # def check(cls, v: "TxParams", **kwargs: Any) -> "TxParams":
    #     match(v.type):
    #         case [0, 1]:
    #             if v.gas_price is None:
    #                 raise ValueError(
    #                     f"gas_price cant be None when type is {v.type}"
    #                 )
    #         case 2:
    #             if v.max_fee_per_gas is None or \
    #                     v.max_priority_fee_per_gas is None:
    #                 raise ValueError(
    #                     "max_fee_per_gas or max_priority_fee_per_gas cant "
    #                     f"be None when type is {v.type}"
    #                 )
    #         case _:
    #             raise ValueError(f"Unsupport transaction type: {v.type}")
    #     return v

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
        frozen = True
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
    access_list: AccessList = Field([], alias="accessList")
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


class BlockHeader(BaseModel):
    difficulty: IntStr
    extra_data: HexBytes = Field(alias="extraData")
    gas_limit: Gas = Field(alias="gasLimit")
    gas_used: Gas = Field(alias="gasUsed")
    base_fee_per_gas: Wei = Field(alias="baseFeePerGas")
    logs_bloom: HexBytes = Field(alias="logsBloom")
    miner: Address
    nonce: HexBytes
    number: BlockNumber
    parent_hash: Hash32 = Field(alias="parentHash")
    hash: Hash32
    mix_hash: Hash32 = Field(alias="mixHash")
    receipts_root: HexBytes = Field(alias="receiptsRoot")
    sha3_uncles: HexBytes = Field(alias="sha3Uncles")
    state_root: HexBytes = Field(alias="stateRoot")
    timestamp: int
    transactions_root: HexBytes = Field(alias="transactionsRoot")
    # vaildators
    int_val = convert.int_validator(
        "difficulty", "gas_limit", "gas_used", "base_fee_per_gas", "number",
        "timestamp"
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        frozen = True
        json_loads = orjson.loads
        json_dumps = json.orjson_dumps


# class Block(BaseModel):
#     baseFeePerGas: Wei
#     difficulty: int
#     extraData: HexBytes
#     gasLimit: int
#     gasUsed: int
#     hash: HexBytes
#     logsBloom: HexBytes
#     miner: ChecksumAddress
#     mixHash: HexBytes
#     nonce: HexBytes
#     number: BlockNumber
#     parentHash: HexBytes
#     receiptsRoot: HexBytes
#     sha3Uncles: HexBytes
#     size: int
#     stateRoot: HexBytes
#     timestamp: Timestamp
#     totalDifficulty: int
#     # list of tx hashes or of txdatas
#     transactions: Union[Sequence[HexBytes], Sequence[Transaction]]
#     transactionsRoot: HexBytes
#     uncles: Sequence[HexBytes]


# class Block(BaseModel):
#     """A published Ethereum block."""
#     number: int
#     """The number of this block, starting at 0 for the genesis block."""
#     hash:  HexBytes
#     """The hash (32 bytes) of this block."""
#     parent_hash: HexBytes
#     """The hash (32 bytes) of the parent block of this block."""
#     nonce: HexBytes
#     """The block nonce, a sequence (8 bytes) determined by the miner."""
#     txns_root: HexBytes
#     """The keccak256 hash (32 bytes) of the root of the trie of transactions in
#         this block.
#     """
#     txns_cnt: int
#     """The number of transactions in this block."""
#     state_root: HexBytes
#     """The keccak256 hash (32 bytes) of the state trie after this block was
#         processed.
#     """
#     receipts_root: HexBytes
#     """The keccak256 hash (32 bytes) of the trie of transaction receipts in
#         this block.
#     """
#     miner: HexBytes
#     """The address (20 bytes) of the account that mined this block."""
#     extra_data: HexBytes
#     """An arbitrary data field supplied by the miner. After the Merge
#         (15537394), this value is always empty bytes.
#     """
#     gas_limit: int
#     """The maximum amount of gas that was available to transactions in this
#         block.
#     """
#     gas_used: int
#     """The amount of gas that was used executing transactions in this block."""
#     base_fee_per_gas: int | None
#     """The fee per unit of gas burned by the protocol in this block. Before
#         EIP-1559 (12965000), this value is always None.
#     """
#     next_base_fee_per_gas: int | None
#     """The fee per unit of gas which needs to be burned in the next block.
#         Before EIP-1559 (12964999), this value is always None.
#     """
#     timestamp: int
#     """The unix timestamp at which this block was mined."""
#     logs_bloom: HexBytes
#     """A bloom filter that can be used to check if a block may contain log
#         entries matching a filter.
#     """
#     mix_hash: HexBytes
#     """The hash (32 bytes) that was used as an input to the PoW process. After
#         the Merge (15537394), this value is the beacon chain's RANDAO value.
#     """
#     difficulty: int
#     """A measure of the difficulty of mining this block. After the Merge
#         (15537394), this value is always 0.
#     """
#     total_difficulty: int
#     """The sum of all difficulty values up to and including this block. After
#         the Merge (15537394), this value is always 58750003716598352816469.
#     """
#     ommer_cnt: int
#     """The number of ommers (AKA uncles) associated with this block. After the
#     Merge (15537394), this value is always 0.
#     """
#     ommers: list[HexBytes]
#     """A list of the hash (32 bytes) of ommer (AKA uncle) blocks associated
#         with this block. After the Merge (15537394), this is always an empty
#         list.
#     """
#     ommer_hash: HexBytes
#     """The keccak256 hash (32 bytes) of all the ommers (AKA uncles) associated
#         with this block.
#     """
#     transactions: list[HexBytes]
#     """A list of the hash (32 bytes) of transactions associated with this
#         block.
#     """

#     class Config:
#         allow_mutation = False
#         json_encoders = {
#             int: json_utils.int_to_int_or_str,
#             bytes: json_utils.bytes_to_hex
#         }
#         json_loads = orjson.loads
#         json_dumps = json_utils.orjson_dumps


# class Log(BaseModel):
#     """A published Ethereum event log."""
#     index: int
#     """The index of this log in the block."""
#     account_address: HexBytes
#     """The address (20 bytes) of the account which generated this log - this
#         will always be a contract account.
#     """
#     topics: list[HexBytes]
#     """A list of 0-4 indexed topics (32 bytes) for the log."""
#     data: HexBytes
#     """Unindexed data for this log."""
#     txn_hash: HexBytes
#     """The hash (32 bytes) of the transaction that generated this log entry."""

#     class Config:
#         allow_mutation = False
#         json_encoders = {
#             int: json_utils.int_to_int_or_str,
#             bytes: json_utils.bytes_to_hex
#         }
#         json_loads = orjson.loads
#         json_dumps = json_utils.orjson_dumps

