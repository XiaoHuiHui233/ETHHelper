import logging
import os
import random
from logging import FileHandler, Formatter

import dotenv
import pytest
from eth_typing.evm import ChecksumAddress

from ethhelper.connnectors.http import GethHttpConnector

dotenv.load_dotenv()

logger = logging.getLogger(__name__)
fmt = Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")
fh = FileHandler(f"./logs/{__name__}", "w", encoding="utf-8")
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.INFO)

host = os.getenv("HOST", "localhost")
port = int(os.getenv("PORT", "8545"))
connector = GethHttpConnector(f"http://{host}:{port}/", logger)


@pytest.mark.asyncio
class TestHttpTxpool:
    async def test_case1(self) -> None:
        _ = await connector.txpool_inspect()

    async def test_case2(self) -> None:
        for _ in range(10):
            _ = await connector.txpool_content()

    async def test_case3(self) -> None:
        for _ in range(20):
            content = await connector.txpool_content()
            keys: list[ChecksumAddress] = random.sample(
                list(content.queued.keys()), 1
            )
            content = await connector.txpool_content_from(keys[0])
