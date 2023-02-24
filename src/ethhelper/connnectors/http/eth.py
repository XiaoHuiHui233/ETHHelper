import typing
from logging import Logger

from eth_typing import Address as Web3Address
from eth_typing import BlockNumber
from web3.eth.async_eth import AsyncEth
from web3.types import ENS
from web3.types import BlockIdentifier as Web3BlockIdentifier
from web3.types import BlockParams
from web3.types import CallOverride as Web3CallOverride
from web3.types import Nonce

from ...datatypes.base import Address, BlockIdentifier, Gas, Hash32, Wei
from ...datatypes.eth import FeeHistory, SyncStatus, Transaction, TxParams
from ...datatypes.geth import CallOverride
from ...utils.stdtype import HexBytes
from .base import GethHttpWeb3


class GethEthHttp(GethHttpWeb3):
    def __init__(self, host: str, port: int, logger: Logger) -> None:
        super().__init__(host, port, logger)
        self.eth = typing.cast(AsyncEth, self.w3.eth)

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

    def _block_id_transfer(
        self, block_identifier: BlockIdentifier
    ) -> Web3BlockIdentifier:
        if isinstance(block_identifier, Hash32):
            return block_identifier.to_web3()
        return block_identifier

    async def eth_call(
        self,
        transaction: TxParams,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride = {},
        ccip_read_enabled: bool = False,
    ) -> HexBytes:
        block_id = self._block_id_transfer(block_identifier)
        state_over: Web3CallOverride = {}
        for addr in state_override:
            state_over[addr] = state_override[addr].to_hex()
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
        block_id = self._block_id_transfer(block_identifier)
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
        block_id = self._block_id_transfer(block_identifier)
        return Transaction.parse_obj(
            await self.eth.get_transaction_by_block(block_id, index)
        )

    async def eth_get_raw_transaction_by_block(
        self, block_identifier: BlockIdentifier, index: int
    ) -> HexBytes:
        block_id = self._block_id_transfer(block_identifier)
        return HexBytes(
            (
                await self.eth.get_raw_transaction_by_block(block_id, index)
            ).hex()
        )

    async def eth_get_transaction_cnt_by_block(
        self, block_identifier: BlockIdentifier
    ) -> int:
        block_id = self._block_id_transfer(block_identifier)
        return await self.eth.get_block_transaction_count(block_id)

    async def eth_send_transaction(self, transaction: TxParams) -> HexBytes:
        return HexBytes(
            await self.eth.send_transaction(transaction.to_web3())
        )

    async def eth_send_raw_transaction(
        self, transaction: HexBytes
     ) -> HexBytes:
        return HexBytes(
            await self.eth.send_raw_transaction(transaction.value)
        )

    # async def eth_get_block(
    #     self,
    #     block_identifier: BlockIdentifier,
    #     full_transactions: bool = False
    # ) -> BlockData:
    #     block_id = self._block_id_transfer(block_identifier)
    #     return await self.eth.get_block(block_id, full_transactions)

    def _address_transfer(self, address: Address | ENS) -> Web3Address | ENS:
        if isinstance(address, Address):
            return address.to_web3()
        return address

    async def eth_get_balance(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> Wei:
        block_id = self._block_id_transfer(block_identifier)
        addr = self._address_transfer(account)
        return Wei(await self.eth.get_balance(addr, block_id))

    async def eth_get_code(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> HexBytes:
        block_id = self._block_id_transfer(block_identifier)
        addr = self._address_transfer(account)
        return HexBytes((await self.eth.get_code(addr, block_id)).hex())

    # async def eth_get_logs(
    #     self,
    #     filter_params: FilterParams,
    # ) -> List[LogReceipt]:
    #     return await self._get_logs(filter_params)

    async def eth_get_account_nonce(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> Nonce:
        block_id = self._block_id_transfer(block_identifier)
        addr = self._address_transfer(account)
        return await self.eth.get_transaction_count(addr, block_id)

    # async def eth_get_transaction_receipt(self, transaction_hash: _Hash32) -> TxReceipt:
    #     return await self._transaction_receipt(transaction_hash)

    # async def eth_wait_for_transaction_receipt(
    #     self, transaction_hash: _Hash32, timeout: float = 120, poll_latency: float = 0.1
    # ) -> TxReceipt:
    #     async def _wait_for_tx_receipt_with_timeout(
    #         _tx_hash: _Hash32, _poll_latency: float
    #     ) -> TxReceipt:
    #         while True:
    #             try:
    #                 tx_receipt = await self._transaction_receipt(_tx_hash)
    #             except TransactionNotFound:
    #                 tx_receipt = None
    #             if tx_receipt is not None:
    #                 break
    #             await asyncio.sleep(poll_latency)
    #         return tx_receipt

    #     try:
    #         return await asyncio.wait_for(
    #             _wait_for_tx_receipt_with_timeout(transaction_hash, poll_latency),
    #             timeout=timeout,
    #         )
    #     except asyncio.TimeoutError:
    #         raise TimeExhausted(
    #             f"Transaction {HexBytes(transaction_hash) !r} is not in the chain "
    #             f"after {timeout} seconds"
    #         )

    # async def eth_get_storage_at(
    #     self,
    #     account: Union[Address, ChecksumAddress, ENS],
    #     position: int,
    #     block_identifier: Optional[BlockIdentifier] = None,
    # ) -> HexBytes:
    #     return await self._get_storage_at(account, position, block_identifier)

    # async def eth_new_filter(self, params: Optional[Union[str, FilterParams, HexStr]]) -> AsyncFilter:
    #     return await self.eth.filter(params)

    # async def eth_get_filter_changes(self, filter_id: HexStr) -> List[LogReceipt]:
    #     return await self._get_filter_changes(filter_id)

    # async def eth_get_filter_logs(self, filter_id: HexStr) -> List[LogReceipt]:
    #     return await self._get_filter_logs(filter_id)

    # async def eth_uninstall_filter(self, filter_id: HexStr) -> bool:
    #     return await self._uninstall_filter(filter_id)
