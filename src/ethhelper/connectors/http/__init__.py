import logging
from logging import (
    Logger,
)

from .base import (
    GethHttpAbstract,
    GethHttpCustomized,
    GethHttpWeb3,
)
from .custom import (
    GethCustomHttp,
)
from .eth import (
    GethEthHttp,
)
from .graphql import (
    GethGraphQL,
)
from .net import (
    GethNetHttp,
)
from .txpool import (
    GethTxpoolHttp,
)


class GethHttpConnector(GethGraphQL, GethCustomHttp):
    """``GethHttpConnector`` is an asynchronous wrapper for all HTTP interfaces
    supported by ETHHelper.

    Due to the flat design style, all interfaces use a simple naming structure
    as the member methods of this class.

    The ``url`` is used to indicate the path of the HTTP service of the Geth
    node, usually in the form of ``http://host:port/``. The use of third-party
    nodes may be out of the ordinary.

    The ``logger`` is used to assign a logger of the Python logging module to
    this class. Explicitly assigning a logger can be used to control the output
    location of the logger, which is convenient for debugging. If this
    parameter is not provided or ``None`` is giving, this class will
    automatically call ``logging.getLogger("GethHttpConnector")`` to generate a
    default logger.

    The ``graphql_url`` is used to specify the URL for the GraphQL interface of
    the Geth node, usually in the form of ``http://host:port/graphql``. If not
    provided, it will generate from ``url`` by appending ``/graphql``.
    """
    def __init__(
        self,
        url: str,
        logger: Logger | None = None,
        graphql_url: str | None = None
    ) -> None:
        if logger is None:
            logger = logging.getLogger("GethHttpConnector")
        super().__init__(url, logger, graphql_url=graphql_url)



__all__ = [
    "GethHttpAbstract",
    "GethHttpCustomized",
    "GethHttpWeb3",
    "GethCustomHttp",
    "GethEthHttp",
    "GethNetHttp",
    "GethTxpoolHttp",
    "GethHttpConnector",
    "GethGraphQL"
]
