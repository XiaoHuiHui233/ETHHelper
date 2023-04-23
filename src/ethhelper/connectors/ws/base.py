
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


class GethSubscriber(metaclass=ABCMeta):
    """Abstract base class for implementing a subscriber to a Geth node using
    websockets with the Geth JSON-RPC API.

    This class defines the basic structure for implementing a subscriber to a
    Geth node using websockets. It provides a method for binding to the node,
    sending requests, handling responses, and closing the connection.

    The ``url`` is used to indicate the path of the WS service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """
    def __init__(self, url: str, logger: Logger) -> None:
        self.url = url
        self.logger = logger
        self.run_task: Task[None] | None = None
        self.closed = False

    async def bind(self) -> Task[None]:
        """Bind the subscriber to the Geth node and start listening for
        messages.

        Returns:
            A task that will run the subscriber until it is closed.
        """
        if self.closed:
            self.logger.error("Cant rebind closed subsriber!")
            raise ValueError("Cant rebind closed subsriber!")
        self.run_task = asyncio.create_task(self.run())
        return self.run_task

    async def run(self) -> None:
        """The main loop that listens for messages from the Geth node."""
        while not self.closed:
            self.id = 0
            try:
                async with client.connect(self.url) as self.ws:
                    self.recv_loop = asyncio.create_task(self._recieve_loop())
                    await self.after_connection()
                    await self.recv_loop
                    exce = self.recv_loop.exception()
                    if exce is not None:
                        self.logger.warning(
                            "Error when recv in Websocket. Retry is 5s."
                        )
                        self.logger.debug(
                            f"Details: {traceback.format_exception(exce)}"
                        )
                        await asyncio.sleep(5)
            except Exception:
                self.logger.warning(
                    "Websocket connection is dead. Retry is 5s."
                )
                self.logger.debug(f"Details: {traceback.format_exc()}")
                await asyncio.sleep(5)

    async def send(self, method: str, params: list[Any]) -> int:
        """Send a request to the Geth node over the websocket connection.

        Args:
            method: The JSON-RPC method to call.
            params: The parameters to send with the request.

        Returns:
            The ID of the request, which can be used to match responses with
            requests.
        """
        self.id += 1
        data = GethRequest(id=self.id, method=method, params=params).json()
        self.logger.debug(f"SEND {data}")
        await self.ws.send(data)
        return self.id

    async def _recieve_loop(self) -> None:
        """The loop that listens for messages from the Geth node."""
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
        """Subscribe to a specific event or method on the Geth node.
        
        Args:
            param: The name of the event or method to subscribe to.

        Returns:
            The ID of the subscription, which can be used to unsubscribe later.
        """
        return await self.send("eth_subscribe", [param])

    @abstractmethod
    async def after_connection(self) -> None:
        """A method that is called after the connection to the Geth node has
        been established.

        This method can be overridden to perform any necessary setup or
        initialization after the connection to the Geth node has been
        established.
        """
        raise NotImplementedError

    @abstractmethod
    async def handle(self, data: GethWSResponse | GethSuccessResponse) -> None:
        """A method that is called when a message is received from the Geth
        node.

        This method must be overridden to handle the messages received from the
        Geth node.

        Args:
            data: The message received from the Geth node.
        """
        raise NotImplementedError

    async def close(self) -> None:
        """Close the connection to the Geth node."""
        if self.closed:
            return
        self.closed = True
        if self.run_task is None:
            return
        await self.ws.close()
        self.recv_loop.cancel()
        self.run_task.cancel()
        try:
            await self.run_task
        except CancelledError:
            pass
