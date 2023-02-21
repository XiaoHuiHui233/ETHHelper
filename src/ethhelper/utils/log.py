import logging
from logging import FileHandler, Formatter, Logger, StreamHandler

set_debug: bool | None = None


def get_logger(
    name: str,
    path: str | None = None,
    console: bool = True,
    fmt_str: str = "%(asctime)s [%(name)s][%(levelname)s] %(message)s"
) -> Logger:
    logger = Logger(name)
    fmt = Formatter(fmt_str)
    if path is not None:
        fh = FileHandler(path, "w", encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    if console:
        sh = StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        logger.addHandler(sh)
    if set_debug is not None:
        logger.setLevel(logging.DEBUG if set_debug else logging.INFO)
    return logger


def debug_mode(on: bool = True) -> None:
    global set_debug
    if set_debug is not None:
        raise ValueError("Debug mode can only be set once!")
    loggers = [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    if on:
        for logger in loggers:
            logger.setLevel(logging.DEBUG)
    else:
        for logger in loggers:
            logger.setLevel(logging.INFO)
    set_debug = on
