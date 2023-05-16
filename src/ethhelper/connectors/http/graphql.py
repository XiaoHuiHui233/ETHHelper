from logging import (
    Logger,
)
import typing
from typing import (
    Any,
)

from eth_typing import (
    BlockNumber,
)
from httpx import (
    AsyncClient,
)
import orjson

from ethhelper.datatypes.geth import (
    GethGraphQLError,
)

from .base import (
    GethHttpAbstract,
)


class GethGraphQL(GethHttpAbstract):
    """A GraphQL interface for Geth nodes that inherits from
    ``GethHttpAbstract``. Provides additional functionalities to access Geth
    nodes via HTTP and GraphQL.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.

    The ``graphql_url`` is used to specify the URL for the GraphQL interface of
    the Geth node, usually in the form of ``http://host:port/graphql``. If not
    provided, it will generate from ``url`` by appending ``/graphql``.
    """
    def __init__(
        self, url: str, logger: Logger, graphql_url: str | None = None
    ) -> None:
        super().__init__(url, logger)
        if graphql_url is None:
            if not url.endswith("/"):
                url += "/"
            self.graphql_url = url + "graphql"
        else:
            self.graphql_url = graphql_url

    async def send_query(self, query: str) -> dict[str, Any]:
        """
        Sends a GraphQL query to the Geth node.

        Args:
            query: The GraphQL query string.

        Returns:
            A dictionary containing the result of the GraphQL query.

        Raises:
            GethGraphQLError: If the Geth node returns an error.
        """
        self.logger.debug(f"SEND GRAPHQL QUERY {query}")
        async with AsyncClient() as client:
            res = await client.post(
                f"{self.graphql_url}",
                content=orjson.dumps({ "query": query}).decode(),
                headers={"Content-Type": "application/json"}
            )
            self.logger.debug(f"RECV GRAPHQL RESULT {res.text}")
            result = orjson.loads(res.text)
            if "error" in result:
                raise GethGraphQLError(
                    typing.cast(list[str], result["error"]["msg"]),
                    typing.cast(dict[str, Any], result["data"]),
                )
            return result["data"]

    async def get_block_ts_by_number(self, height: BlockNumber) -> int:
        """
        Retrieves the timestamp of a block by its block number.

        Args:
            height: The block number.

        Returns:
            The timestamp of the block as an integer.

        Raises:
            GethGraphQLError: If the Geth node returns an error.
        """
        query = """
        query {
            block (number: %d) {
                timestamp
            }
        }
        """ % (height)
        result = await self.send_query(query)
        return int(result["block"]["timestamp"], 0)

    async def get_blocks_ts_by_numbers_range(
        self,
        from_height: BlockNumber,
        to_height: BlockNumber,
        step: int = 5000
    ) -> dict[BlockNumber, int]:
        """
        Retrieves the timestamps of blocks within a range of block numbers.

        Args:
            from_height: The starting block number.
            to_height: The ending block number.
            step: The maximum number of blocks per request.

        Returns:
            A dictionary mapping block numbers to their corresponding
            timestamps.

        Raises:
            GethGraphQLError: If the Geth node returns an error.
        """
        total = to_height - from_height
        if total > step:
            result: dict[BlockNumber, int] = {}
            self.logger.info(
                f"Try to get {total + 1} blocks timestamp, "
                f"call per {step} blocks"
            )
            for i in range(from_height, to_height, 5001):
                if i + step < to_height:
                    result |= await self.get_blocks_ts_by_numbers_range(
                        BlockNumber(i), BlockNumber(i + step)
                    )
                    self.logger.info(
                        "Get blocks timestamp process: "
                        f"{((i + step - from_height + 1)/(total + 1)*100):.2f}"
                        " %"
                    )
                else:
                    result |= await self.get_blocks_ts_by_numbers_range(
                        BlockNumber(i), to_height
                    )
                    self.logger.info("Get blocks timestamp process: 100 %")
        else:
            query = """
            query {
                blocks (from: %d, to: %d) {
                    number
                    timestamp
                }
            }
            """ % (from_height, to_height)
            r = await self.send_query(query)
            result = {d["number"]: int(d["timestamp"], 0) for d in r["blocks"]}
        return result
