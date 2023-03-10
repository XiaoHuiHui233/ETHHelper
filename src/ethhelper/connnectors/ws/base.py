
from abc import (
    ABCMeta,
    abstractmethod,
)
import asyncio
from asyncio import (
    CancelledError,
    Task,
)
from logging import (
    Logger,
)
import traceback
from typing import (
    Any,
)

from pydantic import (
    ValidationError,
)
from websockets import (
    client,
)

from ethhelper.datatypes.geth import (
    GethError,
    GethErrorResponse,
    GethRequest,
    GethSuccessResponse,
    GethWSResponse,
)


class GethSubsriber(metaclass=ABCMeta):
    def __init__(self, url: str, logger: Logger) -> None:
        self.url = url
        self.logger = logger
        self.run_task: Task[None] | None = None
        self.closed = False

    async def bind(self) -> Task[None]:
        if self.closed:
            self.logger.error("Cant rebind closed subsriber!")
            raise ValueError("Cant rebind closed subsriber!")
        self.run_task = asyncio.create_task(self.run())
        return self.run_task

    async def run(self) -> None:
        while not self.closed:
            self.id = 0
            try:
                async with client.connect(self.url) as self.ws:
                    await self.after_connection()
                    await self._recieve_loop()
            except Exception:
                self.logger.warning(
                    "Websocket connection is dead. Retry is 5s."
                )
                self.logger.debug(f"Details: {traceback.format_exc()}")
                await asyncio.sleep(5)

    async def send(self, method: str, params: list[Any]) -> int:
        self.id += 1
        data = GethRequest(id=self.id, method=method, params=params).json()
        self.logger.debug(f"SEND {data}")
        await self.ws.send(data)
        return self.id

    async def _recieve_loop(self) -> None:
        async for data in self.ws:
            if isinstance(data, bytes):
                data = data.decode()
            self.logger.debug(f"RECV {data}")
            response: GethWSResponse | GethSuccessResponse | GethErrorResponse
            try:
                response = GethWSResponse.parse_raw(data)
            except ValidationError:
                try:
                    response = GethSuccessResponse.parse_raw(data)
                except ValidationError:
                    response = GethErrorResponse.parse_raw(data)
                    raise GethError(error=response.error)
            await self.handle(response)

    async def subscribe(self, param: str) -> int:
        return await self.send("eth_subscribe", [param])

    @abstractmethod
    async def after_connection(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def handle(self, data: GethWSResponse | GethSuccessResponse) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        if self.run_task is None:
            return
        await self.ws.close()
        self.run_task.cancel()
        try:
            await self.run_task
        except CancelledError:
            pass
