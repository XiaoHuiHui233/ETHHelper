from datetime import (
    datetime,
)
from logging import (
    Logger,
)
import traceback
from typing import (
    Any,
    Sequence,
)

from eth_typing import (
    BlockNumber,
)

from ethhelper.datatypes.eth import (
    Address,
    Block,
    FilterParams,
    Hash32,
    Log,
)
from ethhelper.datatypes.geth import (
    GethError,
)

from .eth import (
    GethEthHttp,
)
from .net import (
    GethNetHttp,
)
from .txpool import (
    GethTxpoolHttp,
)


class GethCustomHttp(GethEthHttp, GethNetHttp, GethTxpoolHttp):
    """A customized HTTP interface for Geth nodes that inherits from
    ``GethEthHttp``, ``GethNetHttp``, and ``GethTxpoolHttp``. Provides
    additional functionalities to access Geth nodes via HTTP.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)

    async def test_connection(self) -> bool:
        """Test connectivity to the Geth node via both Web3.py and the
        customized HTTP interface.

        Returns:
            A bool indicating whether the connection to the Geth node is
            successful or not.
        """
        try:
            web3 = await self.is_connected()
            customized = await super(GethTxpoolHttp, self).is_connected()
            self.logger.info(
                f"GethHttpWeb3: {web3}, GethTxpoolHttp: {customized}."
            )
            return web3 and customized
        except Exception:
            self.logger.error("GethCustomHttp can't be running.")
            self.logger.debug(f"Detail: {traceback.format_exc()}")
            return False
    
    async def get_logs(self, filter: FilterParams) -> list[Log]:
        """Retrieve a list of logs from the Geth node using the given
        ``FilterParams``.

        Args:
            filter: A FilterParams object used to specify filter parameters for
                the logs.

        Returns:
            A list of Log objects parsed from the logs returned by the Geth
            node.

        Raises:
            ethhelper.types.GethError: Raised when the Geth node returns an
                error.
        """
        async_filter = await self.eth_filter(filter)
        logs = await async_filter.get_all_entries()
        await self.eth_uninstall_filter(async_filter)
        return [Log.parse_obj(log) for log in logs]

    async def get_logs_by_blocks(
        self,
        start_height: BlockNumber,
        end_height: BlockNumber,
        address: Address | list[Address] | None = None,
        topics: Sequence[Hash32 | Sequence[Hash32]] | None = None,
        step: int = 200
    ) -> list[Log]:
        """Retrieve a list of logs within a range of blocks specified by block
        heights.

        Args:
            start_height: The block height to start retrieving logs from.
            end_height: The block height to stop retrieving logs from.
            address: An address or list of addresses to filter the logs by.
            topics: A list of topics or nested lists of topics to filter the
                logs by.
            step: The maximum number of blocks per request, preventing a single
                request from requiring too much memory and taking too long.

        Returns:
            A list of Log objects parsed from the logs returned by the Geth
            node.

        Raises:
            ethhelper.types.GethError: Raised when the Geth node returns an
                error.
        """
        if end_height - start_height > step:
            results: list[Log] = []
            self.logger.info(
                f"Try to get logs from {start_height} to {end_height}, "
                f"call per {step} blocks"
            )
            for i in range(start_height, end_height + 1, step + 1):
                results += await self.get_logs_by_blocks(
                    BlockNumber(i),
                    BlockNumber(min(end_height, i + step)),
                    address,
                    topics,
                    step
                )
            return results
        else:
            self.logger.info(f"Get logs from {start_height} to {end_height}")
            fliter_params = FilterParams(  # type: ignore
                address = address,
                from_block = start_height,  # type: ignore
                to_block = end_height,  # type: ignore
                topics = topics
            )
            return await self.get_logs(fliter_params)

    async def _binary_search(
        self, start: BlockNumber, end: BlockNumber, target: int
    ) -> BlockNumber:
        """
        Perform binary search to find the block height which is closest to the
        target timestamp.

        Args:
            start: The start block height to search from.
            end: The end block height to search to.
            target: The target timestamp to search for.

        Returns:
            A ``BlockNumber`` instance that represents the block height which
            is closest to the target timestamp.
        """
        middle = (start + end) // 2
        ts = (await self.eth_get_block(BlockNumber(middle))).timestamp
        if end - start <= 1:
            if ts >= target:
                return start
            else:
                return end
        if ts == target:
            return BlockNumber(middle)
        if ts > target:
            return await self._binary_search(
                start, BlockNumber(middle), target
            )
        else:
            return await self._binary_search(BlockNumber(middle), end, target)

    async def get_height_after_ts(self, timestamp: int) -> BlockNumber:
        """
        Get the block height closest to the target timestamp.

        Args:
            timestamp: The target timestamp in seconds since the epoch.

        Returns:
            A ``BlockNumber`` instance that represents the block height closest
            to the target timestamp.
        """
        height_now: int = await self.eth_block_number()
        ts_now = int(datetime.now().timestamp())
        if timestamp >= ts_now:
            return BlockNumber(height_now + 1)
        td = ts_now - timestamp
        pos_lower = height_now - (td // 12) - 5
        pos_upper = height_now - (td // 24) + 5
        if pos_upper > height_now:
            pos_upper = height_now
        return await self._binary_search(
            BlockNumber(pos_lower), BlockNumber(pos_upper), timestamp
        )

    async def get_blocks_by_numbers(
        self, numbers: list[BlockNumber], step: int = 200
    ) -> list[Block]:
        """
        Get the blocks with the given block numbers.

        Args:
            numbers: The block numbers.
            step: The maximum number of blocks per request, preventing a single
                request from requiring too much memory and taking too long.

        Returns:
            A list of ``Block`` instances that represent the blocks with the
            given block numbers.
        """
        if len(numbers) > step:
            results: list[Block] = []
            self.logger.info(
                f"Try to get {len(numbers)} blocks, call per {step} blocks"
            )
            for i in range(0, len(numbers), step):
                results += await self.get_blocks_by_numbers(
                    numbers[i:min(i+step, len(numbers))], step
                )
                self.logger.info(
                    "Get blocks process: "
                    f"{(min(i+step, len(numbers))/len(numbers)*100):.2f} %"
                )
            return results
        else:
            requests: list[tuple[str, list[Any] | None]] = []
            for number in numbers:
                requests.append(("eth_getBlockByNumber", [hex(number), False]))
            success, errors = await self.send_multiple(requests)
            if len(errors) != 0:
                raise GethError(error=[err.error for err in errors])
            return [Block.parse_obj(suc.result) for suc in success]

    async def get_blocks_by_numbers_range(
        self, start: BlockNumber, end: BlockNumber, step: int = 200
    ) -> list[Block]:
        """
        Get the blocks with the given block numbers range.

        Args:
            start: The start block number.
            end: The end block number.
            step: The maximum number of blocks per request, preventing a single
                request from requiring too much memory and taking too long.

        Returns:
            A list of ``Block`` instances that represent the blocks with the
            given block numbers range.
        """
        return await self.get_blocks_by_numbers(
            [BlockNumber(i) for i in range(start, end + 1, 1)], step
        )