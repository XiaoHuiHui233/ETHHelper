from eth_typing import (
    HexAddress,
)

from ethhelper.datatypes.txpool import (
    TxpoolContent,
    TxpoolContentFrom,
    TxpoolInspect,
    TxpoolStatus,
)

from .base import (
    GethHttpCustomized,
)


class GethTxpoolHttp(GethHttpCustomized):
    """A class that provides an interface to interact with the Geth txpool
    using HTTP.

    The ``GethTxpoolHttp`` class inherits from the ``GethHttpCustomized`` class
    and provides methods to interact with the Geth txpool using HTTP.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging.
    """
    async def txpool_status(self) -> TxpoolStatus:
        """Returns an object representing the status of the Geth txpool.

        This function sends a ``txpool_status`` request to the Geth node and
        returns the response as a ``TxpoolStatus`` object.

        Returns:
            A ``TxpoolStatus`` object representing the status of the Geth
            txpool.

        Raises:
            ethhelper.types.GethError: Raised when response is a Geth error.
            ethhelper.types.IdNotMatch: Raised when received response id not
                match request id.
        """
        result = await self.send("txpool_status")
        return TxpoolStatus.parse_obj(result)

    async def txpool_inspect(self) -> TxpoolInspect:
        """Returns an object representing the contents of the Geth txpool.

        This function sends a ``txpool_inspect`` request to the Geth node and
        returns the response as a ``TxpoolInspect`` object.

        Returns:
            A ``TxpoolInspect`` object representing the contents of the Geth
            txpool.

        Raises:
            ethhelper.types.GethError: Raised when response is a Geth error.
            ethhelper.types.IdNotMatch: Raised when received response id not
                match request id.
        """
        result = await self.send("txpool_inspect")
        return TxpoolInspect.parse_obj(result)

    async def txpool_content(self) -> TxpoolContent:
        """Returns an object representing the contents of the Geth txpool.

        This function sends a ``txpool_content`` request to the Geth node and
        returns the response as a ``TxpoolContent`` object.

        Returns:
            A ``TxpoolContent`` object representing the contents of the Geth
            txpool.

        Raises:
            ethhelper.types.GethError: Raised when response is a Geth error.
            ethhelper.types.IdNotMatch: Raised when received response id not
                match request id.
        """
        result = await self.send("txpool_content")
        return TxpoolContent.parse_obj(result)

    async def txpool_content_from(
            self, address: HexAddress) -> TxpoolContentFrom:
        """Returns an object representing the transactions from a specific
        address in the Geth txpool.

        This function sends a ``txpool_contentFrom`` request to the Geth node
        with the specified address and returns the response as a
        ``TxpoolContentFrom`` object.

        Args:
            address: The address to get the transactions from.

        Returns:
            A ``TxpoolContentFrom`` object representing the transactions from
            the specified address in the Geth txpool.

        Raises:
            ethhelper.types.GethError: Raised when response is a Geth error.
            ethhelper.types.IdNotMatch: Raised when received response id not
                match request id.
        """
        result = await self.send("txpool_contentFrom", [address])
        return TxpoolContentFrom.parse_obj(result)
