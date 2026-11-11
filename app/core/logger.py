import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

# Console output
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - "
        "<level>{message}</level>"
    ),
)

# All logs
logger.add(
    LOG_DIR / "scraper.log",
    level="DEBUG",
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    encoding="utf-8",
)

# Errors only
logger.add(
    LOG_DIR / "errors.log",
    level="ERROR",
    rotation="5 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)
