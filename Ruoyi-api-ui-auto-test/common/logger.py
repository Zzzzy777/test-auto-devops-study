import logging
from pathlib import Path

from common.config import LOG_DIR


def get_logger(name: str) -> logging.Logger:
    """Return a project logger with console and UTF-8 file output."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(
        Path(LOG_DIR) / "pytest.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger