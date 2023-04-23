from logging import (
    Logger,
)
from typing import (
    Literal,
)

from eth_typing import (
    BlockNumber,
)
from web3._utils.filters import (
    AsyncFilter,
)
from web3.eth.async_eth import (
    AsyncEth,
)
from web3.types import (
    ENS,
    BlockParams,
    CallOverride as Web3CallOverride,
    Nonce,
)

from ethhelper.datatypes.base import (
    Address,
    BlockIdentifier,
    Gas,
    Hash32,
    HexBytes,
    Wei,
)
from ethhelper.datatypes.eth import (
    Block,
    FeeHistory,
    FilterParams,
    Receipt,
    SyncStatus,
    Transaction,
    TxParams,
)
from ethhelper.datatypes.geth import (
    CallOverride,
)
from ethhelper.utils import (
    convert,
)

from .base import (
    GethHttpWeb3,
)


class GethEthHttp(GethHttpWeb3):
    """Class for interacting with an Ethereum node using HTTP with the Geth
    JSON-RPC API.

    This class extends the GethHttpWeb3 class and provides additional methods
    specifically for interacting with the Ethereum network using the Geth
    JSON-RPC API.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.eth: AsyncEth = self.w3.eth
        """Asynchronous Eth interface for Web3. Used to simplify the access
        path.
        """

    async def eth_accounts(self) -> list[Address]:
        """Get a list of all accounts in the currently connected Ethereum node.

        Returns:
            A list containing the addresses of all accounts in the current
            node.
        """
        return [Address(addr) for addr in await self.eth.accounts]

    async def eth_hashrate(self) -> int:
        """Get the hash rate of the current Ethereum node.

        Returns:
            The hash rate of the Ethereum node.
        """
        return await self.eth.hashrate

    async def eth_block_number(self) -> BlockNumber:
        """Get the latest block number on the current Ethereum node.

        Returns:
            The latest block number on the current Ethereum node.
        """
        return await self.eth.block_number

    async def eth_chain_id(self) -> int:
        """Get the chain ID of the current Ethereum node.
    
        Returns:
            The chain ID of the current Ethereum node.
        """
        return await self.eth.chain_id

    async def eth_gas_price(self) -> Wei:
        """Get the latest average gas price on the current Ethereum node.
    
        Returns:
            The latest average gas price on the current Ethereum node.
        """
        return Wei(await self.eth.gas_price)

    async def eth_max_priority_fee_per_gas(self) -> Wei:
        """Get the latest maximum priority fee per gas unit on the current
        Ethereum node.
    
        Returns:
            The latest maximum priority fee per gas unit on the current
            Ethereum node.
        """
        return Wei(await self.eth.max_priority_fee)

    async def eth_mining(self) -> bool:
        """Check whether the current Ethereum node is mining.

        Returns:
            ``True`` if the current Ethereum node is mining, ``False``
            otherwise.
        """
        return await self.eth.mining

    async def eth_syncing(self) -> SyncStatus | bool:
        """Check whether the current Ethereum node is syncing the blockchain.

        Returns:
            If the current Ethereum node is syncing the blockchain, returns a
            ``SyncStatus`` object; otherwise, returns ``False`` if it has
            completed syncing.
        """
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
        """Retrieve historical fee data for a specified number of the latest
        blocks.
    
        Args:
            block_count: The number of blocks to retrieve.
            newest_block: The parameter or block number of the latest block.
            reward_percentiles: The list of fee percentile values to retrieve.
                Defaults to ``None``.
        
        Returns:
            A ``FeeHistory`` object containing the historical fee data.
        """
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
        """Execute a read-only transaction (which won't change the blockchain
        state) and return the result.

        Args:
            transaction: The transaction parameters.
            block_identifier: The block identifier. Defaults to "latest".
            state_override: The state override object. Defaults to {}.
            ccip_read_enabled: Whether to enable CCIP read. Defaults to
                ``False``.

        Returns:
            The result of the executed transaction as a ``HexBytes`` object.
        """
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
        """Estimate the gas cost of a transaction.

        Args:
            transaction: The transaction parameters.
            block_identifier: The block identifier. Defaults to "latest".

        Returns:
            The estimated gas cost of the transaction as a ``Gas`` object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        return Gas(
            await self.eth.estimate_gas(transaction.to_web3(), block_id)
        )

    async def eth_get_transaction(
        self, transaction_hash: Hash32
    ) -> Transaction:
        """Get information about a specific transaction by its hash.

        Args:
            transaction_hash: The hash of the transaction to retrieve.

        Returns:
            The transaction information as a ``Transaction`` object.
        """
        return Transaction.parse_obj(
            await self.eth.get_transaction(transaction_hash.to_web3())
        )

    async def eth_get_raw_transaction(
        self, transaction_hash: Hash32
    ) -> HexBytes:
        """Get the raw bytes of a specific transaction by its hash.

        Args:
            transaction_hash: The hash of the transaction to retrieve.

        Returns:
            The raw bytes of the transaction as a ``HexBytes`` object.
        """
        return HexBytes(
            (
                await self.eth.get_raw_transaction(transaction_hash.to_web3())
            ).hex()
        )

    async def eth_get_transaction_by_block(
        self, block_identifier: BlockIdentifier, index: int
    ) -> Transaction:
        """Get information about a specific transaction by its block and index.

        Args:
            block_identifier: The block identifier containing the transaction.
            index: The index of the transaction within the block.

        Returns:
            The transaction information as a ``Transaction`` object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        return Transaction.parse_obj(
            await self.eth.get_transaction_by_block(block_id, index)
        )

    async def eth_get_raw_transaction_by_block(
        self, block_identifier: BlockIdentifier, index: int
    ) -> HexBytes:
        """Get the raw bytes of a specific transaction by its block and index.

        Args:
            block_identifier: The block identifier containing the transaction.
            index: The index of the transaction within the block.

        Returns:
            The raw bytes of the transaction as a ``HexBytes`` object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        return HexBytes(
            (
                await self.eth.get_raw_transaction_by_block(block_id, index)
            ).hex()
        )

    async def eth_get_transaction_cnt_by_block(
        self, block_identifier: BlockIdentifier
    ) -> int:
        """Get the number of transactions in a specific block.

        Args:
            block_identifier: The block identifier.

        Returns:
            The number of transactions in the block.
        """
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
        """Get the balance of an Ethereum account.

        Args:
            account: The address or ENS name of the account.
            block_identifier: The block identifier. Defaults to "latest".

        Returns:
            The balance of the account as a ``Wei`` object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return Wei(await self.eth.get_balance(addr, block_id))

    async def eth_get_code(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> HexBytes:
        """Get the bytecode of a contract deployed on the Ethereum network.

        Args:
            account: The address or ENS name of the contract.
            block_identifier: The block identifier. Defaults to "latest".

        Returns:
            The bytecode of the contract as a ``HexBytes`` object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return HexBytes((await self.eth.get_code(addr, block_id)).hex())

    async def eth_get_account_nonce(
        self,
        account: Address | ENS,
        block_identifier: BlockIdentifier = "latest"
    ) -> Nonce:
        """Get the nonce of an Ethereum account.

        Args:
            account: The address or ENS name of the account.
            block_identifier: The block identifier. Defaults to "latest".

        Returns:
            The nonce of the account as a ``Nonce`` object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return await self.eth.get_transaction_count(addr, block_id)

    async def eth_get_block(
        self,
        block_identifier: BlockIdentifier,
        full_transactions: bool = False
    ) -> Block:
        """Get information about a specific block.

        Args:
            block_identifier: The block identifier.
            full_transactions: Whether to include full transaction details.
                Defaults to ``False``.

        Returns:
            Block: The block information as a ``Block`` object.
        """
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
        """Get the value stored at a specific position in an Ethereum account's
        storage.
    
        Args:
            account: The address or ENS name of the account.
            position: The position in storage to retrieve.
            block_identifier: The block identifier. Defaults to "latest".
        
        Returns:
            The value stored at the specified position as a ``HexBytes``
            object.
        """
        block_id = convert.block_id_transfer(block_identifier)
        addr = convert.address_transfer(account)
        return HexBytes(
            await self.eth.get_storage_at(addr, position, block_id)
        )

    async def eth_send_raw_transaction(
        self, transaction: HexBytes
     ) -> Hash32:
        """Send a raw transaction to the Ethereum network.

        Args:
            transaction: The raw transaction as a ``HexBytes`` object.

        Returns:
            The hash of the sent transaction as a ``Hash32`` object.
        """
        return Hash32(
            await self.eth.send_raw_transaction(transaction.value)
        )

    async def eth_wait_for_transaction_receipt(
        self,
        transaction_hash: Hash32,
        timeout: float = 120,
        poll_latency: float = 0.1
    ) -> Receipt:
        """Wait for a transaction to be included in a block and return the
        receipt.

        Args:
            transaction_hash: The hash of the transaction to wait for.
            timeout: The maximum time to wait in seconds. Defaults to ``120``.
            poll_latency: The time between polling attempts in seconds.
                Defaults to ``0.1``.

        Returns:
            The transaction receipt as a ``Receipt`` object.
        """
        return Receipt.parse_obj(
            await self.eth.wait_for_transaction_receipt(
                transaction_hash.to_web3(), timeout, poll_latency
            )
        )

    async def eth_get_transaction_receipt(
        self, transaction_hash: Hash32
    ) -> Receipt:
        """Get the receipt of a specific transaction.

        Args:
            transaction_hash: The hash of the transaction to retrieve the
            receipt for.

        Returns:
            The transaction receipt as a ``Receipt`` object.
        """
        return Receipt.parse_obj(
            await self.eth.get_transaction_receipt(
                transaction_hash.to_web3()
            )
        )

    async def eth_sign(
        self, account: Address | ENS, data: HexBytes
    ) -> HexBytes:
        """Sign data with an Ethereum account.
    
        Args:
            account: The address or ENS name of the account to sign with.
            data: The data to sign as a ``HexBytes`` object.
        
        Returns:
            HexBytes: The signature as a ``HexBytes`` object.
        """
        addr = convert.address_transfer(account)
        return HexBytes(await self.eth.sign(addr, data.value))

    async def eth_filter(
        self, filter: Literal["latest", "pending"] | FilterParams
    ) -> AsyncFilter:
        """Create a filter to watch for specific events on the Ethereum
        network.

        Args:
            filter: The filter specification.

        Returns:
            The created filter as an ``AsyncFilter`` object.
        """
        if isinstance(filter, FilterParams):
            return await self.eth.filter(filter.to_web3())
        else:
            return await self.eth.filter(filter)

    async def eth_uninstall_filter(self, filter: AsyncFilter) -> bool:
        """Uninstall a previously installed filter.

        Args:
            filter: The filter to uninstall.

        Returns:
            ``True`` if the filter was successfully uninstalled, ``False``
            otherwise.
        """
        assert filter.filter_id is not None
        return await self.eth.uninstall_filter(filter.filter_id)
