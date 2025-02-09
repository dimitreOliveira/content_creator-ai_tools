import logging
from typing import Optional

DEFAULT_LOG_LEVEL: int = logging.INFO


def setup_logger(
    name: str, log_level: Optional[int] = DEFAULT_LOG_LEVEL
) -> logging.Logger:
    """
    Sets up a logger with the specified name and level.

    Args:
        name: The name of the logger.
        log_level: The logging level (e.g., logging.INFO, logging.DEBUG).
                   Defaults to DEFAULT_LOG_LEVEL if not specified.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
