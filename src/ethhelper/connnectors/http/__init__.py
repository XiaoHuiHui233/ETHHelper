import logging
from logging import (
    Logger,
)

from .custom import (
    GethCustomHttp,
)


class GethHttpConnector(GethCustomHttp):
    def __init__(self, url: str, logger: Logger | None = None) -> None:
        if logger is None:
            logger = logging.getLogger("GethHttpConnector")
        super().__init__(url, logger)


__all__ = ["GethHttpConnector"]
