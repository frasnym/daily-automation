import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with the specified name.
    """
    logger = logging.getLogger(name)
    if (
        not logger.hasHandlers()
    ):  # Avoid adding multiple handlers if the logger is reused
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
