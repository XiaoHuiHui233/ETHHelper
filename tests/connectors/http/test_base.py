import os

import dotenv
import pytest

from ethhelper.connnectors.http import GethHttpConnector

dotenv.load_dotenv()


connector = GethHttpConnector(
    os.getenv("HOST", "localhost"), int(os.getenv("PORT", "8545"))
)


@pytest.mark.asyncio
class TestHttpBase:
    async def test_case1(self) -> None:
        print("connection", await connector.test_connection())

    async def test_case2(self) -> None:
        print("txpool status", await connector.txpool_status())
