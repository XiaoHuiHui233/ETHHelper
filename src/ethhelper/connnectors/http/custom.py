from datetime import (
    datetime,
)
from logging import (
    Logger,
)
import traceback

from eth_typing import (
    BlockNumber,
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
