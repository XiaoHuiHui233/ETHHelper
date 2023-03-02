import abc
from abc import (
    ABCMeta,
)
from logging import (
    Logger,
)
import traceback
from typing import (
    Any,
)

from httpx import (
    AsyncClient,
)
from pydantic import (
    ValidationError,
)
from web3 import (
    AsyncHTTPProvider,
    AsyncWeb3,
)

from ethhelper.datatypes.geth import (
    GethError,
    GethErrorResponse,
    GethRequest,
    GethSuccessResponse,
    IdNotMatch,
)


class GethHttpAbstract(metaclass=ABCMeta):
    def __init__(self, url: str, logger: Logger) -> None:
        self.url = url
        self.logger = logger

    @abc.abstractmethod
    async def is_connected(self) -> bool:
        raise NotImplementedError()


class GethHttpCustomized(GethHttpAbstract):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.id = 0

    async def send(self, method: str, params: list[Any] | None = None) -> Any:
        if params is None:
            params = []
        self.logger.debug(f"SEND {method} {params}")
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
            self.logger.debug(f"RECV {res.text}")
            response: GethSuccessResponse | GethErrorResponse
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
            self.logger.info("GethHttpCustomized is good for connection.")
            return True
        except Exception:
            self.logger.warning(
                f"GethHttpCustomized cannot connect to {self.url}."
            )
            self.logger.debug(f"Detail: {traceback.format_exc()}")
            return False


class GethHttpWeb3(GethHttpAbstract):
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.w3 = AsyncWeb3(AsyncHTTPProvider(self.url))

    async def is_connected(self) -> bool:
        connected = self.w3.is_connected()
        if isinstance(connected, bool):
            self.logger.fatal("GethHttpWeb3 is not running in asyncio!")
            raise NotImplementedError(
                "GethHttpWeb3 is not running in asyncio!"
            )
        return await connected
