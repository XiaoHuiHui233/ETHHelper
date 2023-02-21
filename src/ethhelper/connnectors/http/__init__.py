import traceback

from ...utils import log
from .base import GethHttpCustomized, GethHttpWeb3
from .eth import GethEthHttp
from .net import GethNetHttp
from .txpool import GethTxpoolHttp

logger = log.get_logger(__name__, "./logs/connectors/http.log", False)


class GethHttpConnector(GethEthHttp, GethNetHttp, GethTxpoolHttp):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)

    async def test_connection(self) -> bool:
        try:
            web3 = await super(GethHttpWeb3, self).is_connected()
            customized = await super(GethHttpCustomized, self).is_connected()
            logger.info(
                f"GethHttpWeb3: {web3}, GethHttpCustomized: {customized}."
            )
            return web3 and customized
        except Exception:
            logger.error("HttpGethConnector can't be running.")
            logger.debug(f"Detail: {traceback.format_exc()}")
            return False


__all__ = ["GethHttpConnector"]
