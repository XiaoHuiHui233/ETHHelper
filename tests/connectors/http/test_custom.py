from datetime import (
    datetime,
)
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
from ethhelper.types import (
    Address,
    FilterParams
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
class TestHttpCustom:
    async def test_case1(self) -> None:
        height = await connector.eth_block_number()
        logs = await connector.get_logs(
            FilterParams(  # type: ignore
                address=Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"),
                fromBlock=height-1000,
                toBlock=height,
            )
        )
        logger.info(f"{len(logs)}")

    async def test_case2(self) -> None:
        height = await connector.get_height_after_ts(
            int(datetime(2023, 3, 21, 16, 14).timestamp())
        )
        logger.info(height)
        assert height == 16874761
    
    async def test_case3(self) -> None:
        blocks = await connector.get_blocks_by_numbers(
            BlockNumber(16798774),
            BlockNumber(16798775)
        )
        assert len(blocks) == 2
    
    async def test_case4(self) -> None:
        blocks = await connector.get_blocks_by_numbers(
            BlockNumber(16798774),
            BlockNumber(16799185)
        )
        assert len(blocks) == 16799185 - 16798774 + 1
    
    async def test_case5(self) -> None:
        logs = await connector.get_logs_by_blocks(
            BlockNumber(16798774),
            BlockNumber(16799185),
            Address("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"),
        )
        logger.info(f"{len(logs)}")
