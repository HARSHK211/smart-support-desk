import logging
import os

# Create logs directory
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("smart_support_desk")

logger.setLevel(logging.DEBUG)

# Prevent duplicate logs
logger.propagate = False

# Avoid adding handlers multiple times
if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(filename)s | %(funcName)s | Line %(lineno)d | %(message)s"
    )

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # App Log
    file_handler = logging.FileHandler(
        "logs/app.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Error Log
    error_handler = logging.FileHandler(
        "logs/error.log",
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)