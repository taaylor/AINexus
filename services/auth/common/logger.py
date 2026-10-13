import logging
import sys
from pprint import pformat
from typing import Any, Final, override

from loguru import logger

DEFAULT_FORMAT: Final[str] = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "pid=<cyan>{process.id}</cyan> | "
    "<cyan>{name}</cyan> | "
    "<level>{message}</level>"
)
configured: bool = False


class InterceptHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        init_logging()

    @override
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen_importlib = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen_importlib):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def format_record(record: dict[str, Any]) -> str:
    format_string = DEFAULT_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    return format_string + "\n{exception}"


def init_logging() -> None:
    """Configure Loguru once for the Uvicorn logging configuration."""
    global configured
    if configured:
        return

    handler_config: Any = {
        "sink": sys.stdout,
        "level": logging.INFO,
        "format": format_record,
        "diagnose": False,
        "enqueue": True,
    }
    logger.configure(handlers=[handler_config])
    configured = True
