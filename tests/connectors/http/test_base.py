import logging
from logging import (
    FileHandler,
    Formatter,
)
import os

import dotenv
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
class TestHttpBase:
    async def test_case1(self) -> None:
        logger.info(f"connection {await connector.test_connection()}")

    async def test_case2(self) -> None:
        logger.info(f"txpool status {await connector.txpool_status()}")
