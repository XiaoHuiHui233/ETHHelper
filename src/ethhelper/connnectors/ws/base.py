
import abc
import asyncio
import traceback
from abc import ABCMeta
from asyncio import CancelledError, Task
from logging import Logger
from typing import Any

from pydantic import ValidationError
from websockets import client

from ...datatypes.geth import (GethError, GethErrorResponse, GethRequest,
                               GethSuccessResponse, GethWSResponse)


class GethSubsriber(metaclass=ABCMeta):
    def __init__(self, host: str, port: int, logger: Logger) -> None:
        self.url = f"ws://{host}:{port}/"
        self.logger = logger
        self.run_task: Task[None] | None = None
        self.closed = False

    async def bind(self) -> None:
        if self.closed:
            self.logger.error("Cant rebind closed subsriber!")
            raise ValueError("Cant rebind closed subsriber!")
        self.run_task = asyncio.create_task(self.run())

    async def run(self) -> None:
        while not self.closed:
            self.id = 0
            try:
                async with client.connect(self.url) as self.ws:
                    recieve_task = asyncio.create_task(self._recieve_loop())
                    await self.after_connection()
                    await recieve_task
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

    @abc.abstractmethod
    async def after_connection(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
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
