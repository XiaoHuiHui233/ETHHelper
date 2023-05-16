import logging
from logging import (
    FileHandler,
    Formatter,
)
import os

import dotenv
from eth_typing import (
    BlockNumber,
)
import pytest

from ethhelper import (
    GethHttpConnector,
)

dotenv.load_dotenv()

logger = logging.getLogger(__name__)
fmt = Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")
fh = FileHandler(f"./logs/{__name__}", "w", encoding="utf-8")
fh.setFormatter(fmt)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

host = os.getenv("HOST", "localhost")
port = int(os.getenv("PORT", "8545"))
connector = GethHttpConnector(f"http://{host}:{port}/", logger)


@pytest.mark.asyncio
class TestGraphQL:
    async def test_case1(self) -> None:
        ts = await connector.get_block_ts_by_number(BlockNumber(16798774))
        assert ts == 1678464011
    
    async def test_case2(self) -> None:
        blocks = await connector.get_blocks_ts_by_numbers_range(
            BlockNumber(16798774),
            BlockNumber(16798775)
        )
        assert len(blocks) == 2
    
    async def test_case3(self) -> None:
        blocks = await connector.get_blocks_ts_by_numbers_range(
            BlockNumber(16798774),
            BlockNumber(16799185)
        )
        assert len(blocks) == 16799185 - 16798774 + 1
    
    async def test_case4(self) -> None:
        blocks = await connector.get_blocks_ts_by_numbers_range(
            BlockNumber(16798774),
            BlockNumber(16799185),
            step=20
        )
        assert len(blocks) == 16799185 - 16798774 + 1

    async def test_case5(self) -> None:
        blocks = await connector.get_blocks_ts_by_numbers_range(
            BlockNumber(16798774),
            BlockNumber(16799785),
            step=400
        )
        assert len(blocks) == 16799785 - 16798774 + 1
