from abc import (
    abstractmethod,
)
from logging import (
    Logger,
)

from ethhelper.datatypes.eth import (
    Block,
)
from ethhelper.datatypes.geth import (
    GethSuccessResponse,
    GethWSResponse,
    NoSubscribeToken,
)

from .base import (
    GethSubsriber,
)


class GethNewBlockSubsriber(GethSubsriber):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.wait_first = True

    async def subscribe_new_block(self) -> None:
        self.subscribe_id = await self.subscribe("newHeads")

    async def after_connection(self) -> None:
        await self.subscribe_new_block()
        self.wait_first = True

    async def handle(self, data: GethWSResponse | GethSuccessResponse) -> None:
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
