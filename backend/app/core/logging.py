import logging
import re
import sys
from typing import Any

# Pattern to mask sensitive keys or tokens in log strings
SENSITIVE_PATTERN = re.compile(
    r"(token|secret|key|password|bearer|auth)=['\"]?([^'\"\s]+)['\"]?",
    re.IGNORECASE,
)


class MaskingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return SENSITIVE_PATTERN.sub(r"\1=***", original)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            MaskingFormatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

