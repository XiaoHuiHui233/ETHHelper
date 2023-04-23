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
        """Subscribe to new block notifications on the Geth node."""
        self.subscribe_id = await self.subscribe("newHeads")

    async def after_connection(self) -> None:
        """A method that is called after the connection to the Geth node has
        been established.

        This method is overridden to wait for the Geth node to finish syncing
        and then subscribe to new block notifications.
        """
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
        """A method that is called when a message is received from the Geth
        node.

        This method is overridden to handle new block notifications from the
        Geth node.

        Args:
            data: The message received from the Geth node.
        """
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
        """A method that is called when a new block notification is received
        from the Geth node.

        This method must be overridden to handle new block notifications from
        the Geth node.

        Args:
            block: The new block that was received from the Geth node.
        """
        raise NotImplementedError

    async def on_other(self, data: GethSuccessResponse) -> None:
        """A method that is called when a non-new-block message is received
        from the Geth node.

        This method can be overridden to handle non-new-block messages from the
        Geth node.

        Args:
            data: The message received from the Geth node.
        """
        pass
