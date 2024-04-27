"""Logger for tiny CI/CD pipelines."""

import logging


class Logger:
    """Logger class for tiny CI/CD pipelines."""
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        # Check if handlers already exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, message, severity="info"):
        """Log a message with a given severity."""
        if severity == "info":
            self.logger.info(message)
        elif severity == "warning":
            self.logger.warning(message)
        elif severity == "error":
            self.logger.error(message)
        elif severity is None:
            self.logger.info(message)
        
