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
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)

    async def test_connection(self) -> bool:
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
        async_filter = await self.eth_filter(filter)
        logs = await async_filter.get_all_entries()
        await self.eth_uninstall_filter(async_filter)
        return [Log.parse_obj(log) for log in logs]

    async def get_logs_by_blocks(
        self,
        start_height: BlockNumber,
        end_height: BlockNumber,
        address: Address | list[Address] | None = None,
        topics: Sequence[Hash32 | Sequence[Hash32]] | None = None
    ) -> list[Log]:
        if end_height - start_height > 200:
            results: list[Log] = []
            for i in range(start_height, end_height + 1, 201):
                if i + 200 > end_height:
                    results += await self.get_logs_by_blocks(
                        BlockNumber(i), end_height, address, topics
                    )
                else:
                    results += await self.get_logs_by_blocks(
                        BlockNumber(i), BlockNumber(i + 200), address, topics
                    )
            return results
        else:
            fliter_params = FilterParams(  # type: ignore
                address = address,
                from_block = start_height,  # type: ignore
                to_block = end_height,  # type: ignore
                topics = topics
            )
            return await self.get_logs(fliter_params)

    async def _binary_search(
        self, start: BlockNumber, end: BlockNumber, target: datetime
    ) -> BlockNumber:
        middle = (start + end) // 2
        ts = (await self.eth_get_block(BlockNumber(middle))).timestamp
        dt = datetime.fromtimestamp(ts)
        if end - start <= 1:
            if dt >= target:
                return start
            else:
                return end
        if dt == target:
            return BlockNumber(middle)
        if dt > target:
            return await self._binary_search(
                start, BlockNumber(middle), target
            )
        else:
            return await self._binary_search(BlockNumber(middle), end, target)

    async def get_height_after_dt(self, target: datetime) -> BlockNumber:
        dt_now = datetime.now()
        td = dt_now - target
        height_now: int = await self.eth_block_number()
        pos_lower = height_now - (int(td.total_seconds()) // 12) - 5
        pos_upper = height_now - (int(td.total_seconds()) // 24) + 5
        return await self._binary_search(
            BlockNumber(pos_lower), BlockNumber(pos_upper), target
        )
    
    async def get_blocks_by_numbers(
        self, start: BlockNumber, end: BlockNumber
    ) -> list[Block]:
        if end - start > 200:
            results: list[Block] = []
            for i in range(start, end + 1, 201):
                if i + 200 > end:
                    results += await self.get_blocks_by_numbers(
                        BlockNumber(i), end
                    )
                else:
                    results += await self.get_blocks_by_numbers(
                        BlockNumber(i), BlockNumber(i + 200)
                    )
            return results
        else:
            requests: list[tuple[str, list[Any] | None]] = []
            for i in range(start, end + 1):
                requests.append(("eth_getBlockByNumber", [hex(i), False]))
            success, errors = await self.send_multiple(requests)
            if len(errors) != 0:
                raise GethError(error=[err.error for err in errors])
            return [Block.parse_obj(suc.result) for suc in success]
