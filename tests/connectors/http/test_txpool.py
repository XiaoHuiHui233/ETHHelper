import os
import random

import dotenv
import pytest
from eth_typing.evm import ChecksumAddress

from ethhelper.connnectors.http import GethHttpConnector

dotenv.load_dotenv()


connector = GethHttpConnector(
    os.getenv("HOST", "localhost"), int(os.getenv("PORT", "8545"))
)


@pytest.mark.asyncio
class TestHttpTxpool:
    async def test_case1(self) -> None:
        inspect = await connector.txpool_inspect()
        with open("./tmp/txpool_inspect.json", "w") as wf:
            wf.write(inspect.json())

    async def test_case2(self) -> None:
        for _ in range(10):
            content = await connector.txpool_content()
            with open("./tmp/txpool_content.json", "w") as wf:
                wf.write(content.json())

    async def test_case3(self) -> None:
        for _ in range(20):
            content = await connector.txpool_content()
            keys: list[ChecksumAddress] = random.sample(
                list(content.queued.keys()), 1
            )
            content = await connector.txpool_content_from(keys[0])
            with open("./tmp/txpool_content_from.json", "w") as wf:
                wf.write(content.json())
