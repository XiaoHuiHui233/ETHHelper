import typing
from logging import Logger

from web3.net import AsyncNet

from .base import GethHttpWeb3


class GethNetHttp(GethHttpWeb3):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.net = typing.cast(AsyncNet, self.w3.net)

    async def net_listening(self) -> bool:
        return await self.net.listening

    async def net_peer_count(self) -> int:
        return await self.net.peer_count

    async def net_version(self) -> str:
        return await self.net.version
