import asyncio
import os

import dotenv
import pytest

from ethhelper.connnectors.ws.block import GethNewBlockSubsriber
from ethhelper.datatypes.eth import BlockHeader

dotenv.load_dotenv()


class MySubscriber(GethNewBlockSubsriber):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)

    async def on_block(self, block: BlockHeader) -> None:
        print(block.number)


@pytest.mark.asyncio
class TestHttpBase:
    async def test_case1(self) -> None:
        subscriber = MySubscriber(
            os.getenv("HOST", "localhost"), int(os.getenv("WS_PORT", "8546"))
        )
        await subscriber.bind()
        await asyncio.sleep(24)
        await subscriber.close()
