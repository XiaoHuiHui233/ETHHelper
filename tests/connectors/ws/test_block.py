import asyncio
import logging
import os
from logging import FileHandler, Formatter, Logger

import dotenv
import pytest

from ethhelper.connnectors.ws.block import GethNewBlockSubsriber
from ethhelper.datatypes.eth import BlockHeader

dotenv.load_dotenv()

logger = logging.getLogger(__name__)
fmt = Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")
fh = FileHandler(f"./logs/{__name__}", "w", encoding="utf-8")
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


class MySubscriber(GethNewBlockSubsriber):
    def __init__(self, host: str, port: int, logger: Logger) -> None:
        super().__init__(host, port, logger)

    async def on_block(self, block: BlockHeader) -> None:
        self.logger.info(f"new block {block.number}")


@pytest.mark.asyncio
class TestHttpBase:
    async def test_case1(self) -> None:
        subscriber = MySubscriber(
            os.getenv("HOST", "localhost"),
            int(os.getenv("WS_PORT", "8546")),
            logger
        )
        await subscriber.bind()
        await asyncio.sleep(24)
        await subscriber.close()
