import abc
import traceback
from abc import ABCMeta
from typing import Any

from httpx import AsyncClient
from pydantic import ValidationError
from web3 import AsyncHTTPProvider, Web3

from ...datatypes.geth import (GethErrorDetail, GethErrorResponse, GethRequest,
                               GethSuccessResponse)
from ...utils import log

logger = log.get_logger(__name__, "./logs/connectors/http.log", False)


class IdNotMatch(Exception):
    pass


class GethError(Exception):
    def __init__(self, error: GethErrorDetail) -> None:
        self.code = error.code
        self.msg = error.message
        super().__init__(f"{error.code}: {error.message}")


class GethHttpAbstract(metaclass=ABCMeta):
    def __init__(self, host: str, port: int) -> None:
        self.url = f"http://{host}:{port}/"

    @abc.abstractmethod
    async def is_connected(self) -> bool:
        raise NotImplementedError()


class GethHttpCustomized(GethHttpAbstract):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.id = 0

    async def send(self, method: str, params: list[Any] | None = None) -> Any:
        if params is None:
            params = []
        logger.debug(f"SEND {method} {params}")
        if self.id >= 100000000:
            self.id = 0
        self.id += 1
        id = self.id
        request = GethRequest(id=id, method=method, params=params)
        async with AsyncClient() as client:
            res = await client.post(
                f"{self.url}",
                content=request.json(),
                headers={"Content-Type": "application/json"}
            )
            logger.debug(f"RECV {res.text}")
            try:
                response = GethSuccessResponse.parse_raw(res.text)
                if id != response.id:
                    raise IdNotMatch(
                        f"Send id {id} but received {response.id}"
                    )
            except ValidationError:
                response = GethErrorResponse.parse_raw(res.text)
                raise GethError(error=response.error)
            return response.result

    async def is_connected(self) -> bool:
        try:
            await self.send("net_version")
            logger.info("GethHttpCustomized is good for connection.")
            return True
        except Exception:
            logger.warning(
                f"GethHttpCustomized cannot connect to {self.url}."
            )
            logger.debug(f"Detail: {traceback.format_exc()}")
            return False


class GethHttpWeb3(GethHttpAbstract):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.w3 = Web3(AsyncHTTPProvider(self.url))

    async def is_connected(self) -> bool:
        connected = self.w3.is_connected()
        if isinstance(connected, bool):
            logger.fatal("GethHttpWeb3 is not running in asyncio!")
            raise NotImplementedError(
                "GethHttpWeb3 is not running in asyncio!"
            )
        return await connected
