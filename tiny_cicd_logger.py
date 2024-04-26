"""Logger for tiny CI/CD pipelines."""

import logging

logger = logging.getLogger(__name__)


def setup_logger():
    """Set up the logger."""
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log(message, severity):
    """Log a message."""
    if severity == "info":
        logger.info(message)
    elif severity == "warning":
        logger.warning(message)
    elif severity == "error":
        logger.error(message)
