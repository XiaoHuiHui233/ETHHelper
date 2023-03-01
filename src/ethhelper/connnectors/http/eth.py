from logging import Logger
from typing import Literal

from eth_typing import BlockNumber
from web3._utils.filters import AsyncFilter
from web3.types import ENS, BlockParams
from web3.types import CallOverride as Web3CallOverride
from web3.types import Nonce

from ethhelper.datatypes.base import (
    Address,
    BlockIdentifier,
    Gas,
    Hash32,
    HexBytes,
    Wei
)
from ethhelper.datatypes.eth import (
    Block,
    FeeHistory,
    FilterParams,
    Log,
    Receipt,
    SyncStatus,
    Transaction,
    TxParams
)
from ethhelper.datatypes.geth import CallOverride
from ethhelper.utils import convert

from .base import GethHttpWeb3


class GethEthHttp(GethHttpWeb3):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.eth = self.w3.eth

    async def eth_accounts(self) -> list[Address]:
        return [Address(addr) for addr in await self.eth.accounts]

    async def eth_hashrate(self) -> int:
        return await self.eth.hashrate

    async def eth_block_number(self) -> BlockNumber:
        return await self.eth.block_number

    async def eth_chain_id(self) -> int:
        return await self.eth.chain_id

    async def eth_gas_price(self) -> Wei:
        return Wei(await self.eth.gas_price)

    async def eth_max_priority_fee_per_gas(self) -> Wei:
        return Wei(await self.eth.max_priority_fee)

    async def eth_mining(self) -> bool:
        return await self.eth.mining

    async def eth_syncing(self) -> SyncStatus | bool:
        result = await self.eth.syncing
        if isinstance(result, bool):
            return result
        return SyncStatus.parse_obj(result)

    async def eth_fee_history(
        self,
        block_count: int,
        newest_block: BlockParams | BlockNumber,
        reward_percentiles: list[float] | None = None,
    ) -> FeeHistory:
        return FeeHistory.parse_obj(
            await self.eth.fee_history(
                block_count, newest_block, reward_percentiles
            )
        )

    async def eth_call(
        self,
        transaction: TxParams,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride = {},
        ccip_read_enabled: bool = False,
    ) -> HexBytes:
        block_id = convert.block_id_transfer(block_identifier)
        state_over: Web3CallOverride = {}
        for addr in state_override:
            state_over[addr] = state_override[addr].to_web3()
        return HexBytes(
            (
                await self.eth.call(
                    transaction.to_web3(),
                    block_id,
                    state_over,
                    ccip_read_enabled
                )
            ).hex()
        )

    async def eth_estimate_gas(
        self,
        transaction: TxParams,
        block_identifier: BlockIdentifier = "latest"
    ) -> Gas:
        block_id = convert.block_id_transfer(block_identifier)
        return Gas(
            await self.eth.estimate_gas(transaction.to_web3(), block_id)
        )

    async def eth_get_transaction(
        self, transaction_hash: Hash32
    ) -> Transaction:
        return Transaction.parse_obj(
            await self.eth.get_transaction(transaction_hash.to_web3())
        )

    async def eth_get_raw_transaction(
        self, transaction_hash: Hash32
    ) -> HexBytes:
        return HexBytes(
            (
                await self.eth.get_raw_transaction(transaction_hash.to_web3())
            ).hex()
        )

    async def eth_get_transaction_by_block(
        self, block_identifier: BlockIdentifier, index: int
    ) -> Transaction:
        block_id = convert.block_id_transfer(block_identifier)
        return Transaction.parse_obj(
            await self.eth.get_transaction_by_block(block_id, index)
        )

    async def eth_get_raw_transaction_by_block(
        self, block_identifier: BlockIdentifier, index: int
    ) -> HexBytes:
        block_id = convert.block_id_transfer(block_identifier)
        return HexBytes(
            (
                await self.eth.get_raw_transaction_by_block(block_id, index)
            ).hex()
        )

    async def eth_get_transaction_cnt_by_block(
        self, block_identifier: BlockIdentifier
    ) -> int:
        block_id = convert.block_id_transfer(block_identifier)
        return await self.eth.get_block_transaction_count(block_id)

    async def eth_send_transaction(self, transaction: TxParams) -> HexBytes:
        return HexBytes(
            await self.eth.send_transaction(transaction.to_web3())
        )

    async def eth_get_balance(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> Wei:
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return Wei(await self.eth.get_balance(addr, block_id))

    async def eth_get_code(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> HexBytes:
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return HexBytes((await self.eth.get_code(addr, block_id)).hex())

    async def eth_get_account_nonce(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> Nonce:
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return await self.eth.get_transaction_count(addr, block_id)

    async def eth_get_block(
        self,
        block_identifier: BlockIdentifier,
        full_transactions: bool = False
    ) -> Block:
        block_id = convert.block_id_transfer(block_identifier)
        return Block.parse_obj(
            await self.eth.get_block(block_id, full_transactions)
        )

    async def eth_get_storage_at(
        self,
        account: Address | ENS,
        position: int,
        block_identifier: BlockIdentifier = "latest",
    ) -> HexBytes:
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return HexBytes(
            await self.eth.get_storage_at(addr, position, block_id)
        )

    async def eth_send_raw_transaction(
        self, transaction: HexBytes
     ) -> Hash32:
        return Hash32(
            await self.eth.send_raw_transaction(transaction.value)
        )

    async def eth_wait_for_transaction_receipt(
        self,
        transaction_hash: Hash32,
        timeout: float = 120,
        poll_latency: float = 0.1
    ) -> Receipt:
        return Receipt.parse_obj(
            await self.eth.wait_for_transaction_receipt(
                transaction_hash.to_web3(), timeout, poll_latency
            )
        )

    async def eth_get_transaction_receipt(
        self, transaction_hash: Hash32
    ) -> Receipt:
        return Receipt.parse_obj(
            await self.eth.get_transaction_receipt(
                transaction_hash.to_web3()
            )
        )

    async def eth_sign(
        self, account: Address | ENS, data: HexBytes
    ) -> HexBytes:
        addr = convert.address_transfer(account)
        return HexBytes(await self.eth.sign(addr, data.value))

    async def eth_filter(
        self, filter: Literal["latest", "pending"] | FilterParams
    ) -> AsyncFilter:
        if isinstance(filter, FilterParams):
            return await self.eth.filter(filter.to_web3())
        else:
            return await self.eth.filter(filter)

    async def eth_uninstall_filter(self, filter: AsyncFilter) -> bool:
        assert filter.filter_id is not None
        return await self.eth.uninstall_filter(filter.filter_id)

    async def get_logs(self, filter: FilterParams) -> list[Log]:
        async_filter = await self.eth_filter(filter)
        logs = await async_filter.get_all_entries()
        await self.eth_uninstall_filter(async_filter)
        return [Log.parse_obj(log) for log in logs]
