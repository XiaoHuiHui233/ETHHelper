from abc import (
    abstractmethod,
)
import asyncio
from asyncio import (
    Event,
)
import logging
from logging import (
    Logger,
)

from ethhelper.datatypes.eth import (
    Block,
)
from ethhelper.datatypes.geth import (
    GethIsDead,
    GethSuccessResponse,
    GethWSResponse,
    NoSubscribeToken,
)

from .base import (
    GethSubscriber,
)


class GethNewBlockSubscriber(GethSubscriber):
    def __init__(self, url: str, logger: Logger | None = None) -> None:
        if logger is None:
            logger = logging.getLogger("GethNewBlockSubsriber")
        super().__init__(url, logger)

    async def subscribe_new_block(self) -> None:
        self.subscribe_id = await self.subscribe("newHeads")

    async def after_connection(self) -> None:
        self.wait_syncing = True
        self.syncing = Event()
        self.wait_first = True
        while self.wait_syncing:
            await self.send("eth_syncing", [])
            self.logger.info("Waiting for the result of syncing")
            await self.syncing.wait()
            if self.wait_syncing:
                self.logger.warning("Geth node is syncing...")
                await asyncio.sleep(5)
        self.logger.info("Geth is synced. Continue.")
        await self.subscribe_new_block()
        

    async def handle(self, data: GethWSResponse | GethSuccessResponse) -> None:
        if self.wait_syncing:
            if not isinstance(data, GethSuccessResponse):
                raise GethIsDead
            if isinstance(data.result, bool) and not data.result:
                self.wait_syncing = False
            self.syncing.set()
            return
        if self.wait_first:
            if not isinstance(data, GethSuccessResponse):
                raise NoSubscribeToken
            if not isinstance(data.result, str):
                raise NoSubscribeToken
            self.subscribe_token = data.result
            self.wait_first = False
            return
        if not isinstance(data, GethWSResponse):
            await self.on_other(data)
            return

        await self.on_block(Block.parse_obj(data.params.result))

    @abstractmethod
    async def on_block(self, block: Block) -> None:
        raise NotImplementedError

    async def on_other(self, data: GethSuccessResponse) -> None:
        pass
