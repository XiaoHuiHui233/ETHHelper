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
import orjson
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
    GethResponse,
    GethSuccessResponse,
    IdNotMatch,
)
from ethhelper.utils import (
    json,
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

    def parse_response(self, raw_res: str) -> GethResponse:
        try:
            response = GethSuccessResponse.parse_raw(raw_res)
        except ValidationError:
            response = GethErrorResponse.parse_raw(raw_res)
        self.logger.debug(f"RECV {response}")
        return response

    def parse_multiple_responses(
        self, raw_res: str
    ) -> tuple[list[GethSuccessResponse], list[GethErrorResponse]]:
        raw_res_list = orjson.loads(raw_res)
        success: list[GethSuccessResponse] = []
        errors: list[GethErrorResponse] = []
        for res in raw_res_list:
            try:
                response = GethSuccessResponse.parse_obj(res)
                success.append(response)
            except ValidationError:
                response = GethErrorResponse.parse_obj(res)
                errors.append(response)
        self.logger.debug(f"RECV MULTIPLE {success} {errors}")
        return success, errors

    async def send_raw(self, raw: str) -> str:
        self.logger.debug(f"SEND RAW {raw}")
        async with AsyncClient() as client:
            res = await client.post(
                f"{self.url}",
                content=raw,
                headers={"Content-Type": "application/json"}
            )
            self.logger.debug(f"RECV RAW {res.text}")
            return res.text

    async def send(self, method: str, params: list[Any] | None = None) -> Any:
        if params is None:
            params = []
        self.logger.debug(f"SEND {method} {params}")
        if self.id >= 100000000:
            self.id = 0
        self.id += 1
        id = self.id
        request = GethRequest(id=id, method=method, params=params)
        raw_res = await self.send_raw(request.json())
        response = self.parse_response(raw_res)
        if isinstance(response, GethErrorResponse):
            raise GethError(error=response.error)
        if id != response.id:
            raise IdNotMatch(
                f"Send id {id} but received {response.id}"
            )
        return response.result

    async def send_multiple(
        self, raw_requests: list[tuple[str, list[Any] | None]]
    ) -> tuple[list[GethSuccessResponse], list[GethErrorResponse]]:
        self.logger.debug(f"SEND MULTIPLE {raw_requests}")
        requests: list[GethRequest] = []
        for method, params in raw_requests:
            if self.id >= 100000000:
                self.id = 0
            self.id += 1
            if params is None:
                params = []
            req = GethRequest(id=self.id, method=method, params=params)
            requests.append(req)
        raw_res = await self.send_raw(
            json.orjson_dumps([req.dict() for req in requests])
        )
        return self.parse_multiple_responses(raw_res)

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
