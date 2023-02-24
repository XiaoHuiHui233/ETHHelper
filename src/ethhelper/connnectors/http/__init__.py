import traceback
from logging import Logger

from .eth import GethEthHttp
from .net import GethNetHttp
from .txpool import GethTxpoolHttp


class GethHttpConnector(GethEthHttp, GethNetHttp, GethTxpoolHttp):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)

    async def test_connection(self) -> bool:
        try:
            web3 = await self.is_connected()
            customized = await super(GethTxpoolHttp, self).is_connected()
            self.logger.info(
                f"GethHttpWeb3: {web3}, GethHttpCustomized: {customized}."
            )
            return web3 and customized
        except Exception:
            self.logger.error("HttpGethConnector can't be running.")
            self.logger.debug(f"Detail: {traceback.format_exc()}")
            return False


__all__ = ["GethHttpConnector"]
