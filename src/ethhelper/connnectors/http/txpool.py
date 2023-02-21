from eth_typing import HexAddress

from ...datatypes.txpool import (TxpoolContent, TxpoolContentFrom,
                                 TxpoolInspect, TxpoolStatus)
from .base import GethHttpCustomized


class GethTxpoolHttp(GethHttpCustomized):
    async def txpool_status(self) -> TxpoolStatus:
        result = await self.send("txpool_status")
        return TxpoolStatus.parse_obj(result)

    async def txpool_inspect(self) -> TxpoolInspect:
        result = await self.send("txpool_inspect")
        return TxpoolInspect.parse_obj(result)

    async def txpool_content(self) -> TxpoolContent:
        result = await self.send("txpool_content")
        return TxpoolContent.parse_obj(result)

    async def txpool_content_from(
            self, address: HexAddress) -> TxpoolContentFrom:
        result = await self.send("txpool_contentFrom", [address])
        return TxpoolContentFrom.parse_obj(result)
