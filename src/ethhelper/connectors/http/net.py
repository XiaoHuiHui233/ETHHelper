from logging import (
    Logger,
)

from web3.net import (
    AsyncNet,
)

from .base import (
    GethHttpWeb3,
)


class GethNetHttp(GethHttpWeb3):
    """Class for interacting with a Geth node using HTTP with the Geth JSON-RPC
    API.

    This class extends the GethHttpWeb3 class and provides additional methods
    specifically for interacting with the network using the Geth JSON-RPC API.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """
    def __init__(self, url: str, logger: Logger) -> None:
        super().__init__(url, logger)
        self.net: AsyncNet = self.w3.net
        """Asynchronous Net interface for Web3. Used to simplify the access
        path.
        """

    async def net_listening(self) -> bool:
        """Check if the Geth node is currently listening for connections.

        Returns:
            ``True`` if the node is listening, ``False`` otherwise.
        """
        return await self.net.listening

    async def net_peer_count(self) -> int:
        """Get the number of peers currently connected to the Geth node.

        Returns:
            The number of peers.
        """
        return await self.net.peer_count

    async def net_version(self) -> str:
        """Get the version number of the Geth node.

        Returns:
            str: The version as a string.
        """
        return await self.net.version
