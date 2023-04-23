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
    """A basic abstraction over Geth's HTTP interface wrapper.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """

    def __init__(self, url: str, logger: Logger) -> None:
        self.url: str = url
        """The url giving from the constructor of this class.

            >>> from ethhelper import GethHttpConnector
            >>> connector = GethHttpConnector("http://localhost:8545/")
            >>> connector.url
            'http://localhost:8545/'
        """
        self.logger: Logger = logger
        """The logger giving from the constructor of this class or default by
        ``logging.getLogger("GethHttpConnector")``
        """

    @abc.abstractmethod
    async def is_connected(self) -> bool:
        """Check connectivity.
        
        Subclasses must implement methods to detect connectivity.

        Returns:
            A bool value for connectivity is good or not.
        """
        raise NotImplementedError()


class GethHttpCustomized(GethHttpAbstract):
    """An interface wrapper for direct HTTP access to Geth.

    The `GethHttpCustomized` class provides an interface wrapper that
    allows for direct HTTP access to a Geth node.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """

    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.id: int = 0
        """The id used when sending requests to Geth, an integer starting from
        ``1`` and incrementing for each request. Reset when it exceeds
        ``100000000``.
        """

    def parse_response(self, raw_res: str) -> GethResponse:
        """Parse the content of the Geth node response.

        This function will attempt to parse the input into a
        ``GethSuccessResponse``, and failing that, into a
        ``GethErrorResponse``.

        Args:
            raw_res: the content of the HTTP response of the Geth node in
                string form.
        
        Returns:
            An object of either GethSuccessResponse or GethErrorResponse,
            respectively indicates whether this is a normalized success
            response or an error response.
        
        Raises:
            pydantic.ValidationError: Raised when input data cannot be parsed
                into either GethSuccessResponse or GethErrorResponse.
        """
        try:
            response = GethSuccessResponse.parse_raw(raw_res)
        except ValidationError:
            response = GethErrorResponse.parse_raw(raw_res)
        self.logger.debug(f"RECV {response}")
        return response

    def parse_multiple_responses(
        self, raw_res: str
    ) -> tuple[list[GethSuccessResponse], list[GethErrorResponse]]:
        """Parse the content of the Geth node responses.

        Geth provides an interface that allows multiple Geth requests to be
        served in a single HTTP request. Likewise, the response will be
        multiple. This function is used to parse multiple Geth responses from
        a single HTTP response.

        This function will attempt to parse the input into a list. Afterwards,
        this function assumes that the elements of this list are in the form of
        ``GethSuccessResponse` or ``GethErrorResponse``, and use pydantic to
        parse these elements.

        Args:
            raw_res: the content of the HTTP response of the Geth node in
                string form.

        Returns:
            A tuple with two lists. One is a list of GethSuccessResponse and
            the other one is a list of GethErrorResponse. They respectively
            indicate whether these are normalized success responses or error
            responses.

        Raises:
            orjson.JSONDecodeError: Raised when the raw content cannot be json
                decoded.
            pydantic.ValidationError: Raised when any element in json decoded
                list cannot be parsed into either GethSuccessResponse or
                GethErrorResponse.
        """
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
        """Send json text to Geth node and return text of the response.

        Args:
            raw: The json text will be sent.

        Returns:
            A string of the json content of the response in text.

        Raises:
            httpx.RequestError: Raised when an HTTP request fails.
        """
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
        """Send a Geth request to Geth node and return the data of Geth
        response.

        HTTP communication with Geth follows the JSON-RPC specification. It
        stipulates that each request needs to provide a ``method`` and a series
        of ``parameters``. This function is the encapsulation of this behavior.
        An ``id`` is automatically generated inside the function. The function
        will form a ``GethRequest`` object with the ``id`` and the input
        ``method`` and ``params``, encode it into json text by pydantic and
        send it to the Geth node.

        Args:
            method: The method name of the Geth HTTP interface to call.
            params: A series of parameters used by Geth to make the request.

        Returns:
            A basic type of object that represents the result returned by Geth
            after executing the request.

        Raises:
            httpx.RequestError: Raised when an HTTP request fails.
            ethhelper.types.GethError: Raised when response is a Geth error.
            ethhelper.types.IdNotMatch: Raised when received response id not
                match request id.
        """
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
        """Send multiple Geth requests to the Geth node and return the data of
        the Geth responses.

        HTTP communication with Geth follows the JSON-RPC specification. It
        stipulates that each request needs to provide a ``method`` and a series
        of ``parameters``. This function is the encapsulation of this behavior.
        Multiple requests can be sent in one HTTP request. 

        Args:
            raw_requests: A list of tuples, where each tuple contains a string
                ``method`` and a list of parameters ``params``. The parameters
                can be ``None`` if there are no parameters for the method.

        Returns:
            A tuple with two lists. One is a list of GethSuccessResponse and
            the other one is a list of GethErrorResponse. They respectively
            indicate whether these are normalized success responses or error
            responses.

        Raises:
            httpx.RequestError: Raised when an HTTP request fails.
            orjson.JSONDecodeError: Raised when the raw content cannot be json
                decoded.
            pydantic.ValidationError: Raised when any element in the json
                decoded list cannot be parsed into either GethSuccessResponse
                or GethErrorResponse.
        """
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
        """Checks the connectivity of the Geth node.

        This function checks the connectivity of the Geth node by sending a
        ``net_version`` request to the node. If the request is successful, it
        indicates that the Geth node is available and returns ``True``. If not,
        it returns ``False``. If an exception occurs during the request, the
        function logs a warning and returns ``False``.

        Returns:
            A bool value indicating whether the Geth node is connected and
            available or not.
        """
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
    """A wrapper based on Web3.py to access Geth HTTP interface.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """

    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.w3 = AsyncWeb3(AsyncHTTPProvider(self.url))

    async def is_connected(self) -> bool:
        """Checks the connectivity of the Geth node.

        This function checks the connectivity of the Geth node by calling the
        ``is_connected()`` method of the Web3.py library. If the method returns
        a boolean value, it indicates that the Geth node is available and
        returns ``True``. If not, it returns ``False``. If an exception occurs
        during the request, the function logs a warning and returns ``False``.

        Raises:
            NotImplementedError: If the ``is_connected()`` method of the
                Web3.py library returns a boolean value, it indicates that
                Web3.py is not running in asyncio.

        Returns:
            A bool value indicating whether the Geth node is connected and
            available or not.
        """
        connected = self.w3.is_connected()
        if isinstance(connected, bool):
            self.logger.fatal("GethHttpWeb3 is not running in asyncio!")
            raise NotImplementedError(
                "GethHttpWeb3 is not running in asyncio!"
            )
        return await connected
