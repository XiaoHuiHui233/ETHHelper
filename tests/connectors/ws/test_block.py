import asyncio
import logging
from logging import (
    FileHandler,
    Formatter,
    Logger,
)
import os

import dotenv
import pytest

from ethhelper import (
    GethNewBlockSubscriber,
)
from ethhelper.types import (
    Block,
)

dotenv.load_dotenv()

logger = logging.getLogger(__name__)
fmt = Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")
fh = FileHandler(f"./logs/{__name__}", "w", encoding="utf-8")
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


class MySubscriber(GethNewBlockSubscriber):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)

    async def on_block(self, block: Block) -> None:
        self.logger.info(f"new block {block}")
        self.logger.info(f"new block number {block.number}")


@pytest.mark.asyncio
class TestHttpBase:
    async def test_case1(self) -> None:
        host: str = os.getenv("HOST", "localhost")
        port = int(os.getenv("WS_PORT", "8546"))
        subscriber = MySubscriber(f"ws://{host}:{port}/", logger)
        await subscriber.bind()
        await asyncio.sleep(24)
        await subscriber.close()
