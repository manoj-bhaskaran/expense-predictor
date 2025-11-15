"""
Mock python_logging_framework for testing purposes.

This is a minimal implementation to allow tests to run when the actual
python_logging_framework package cannot be installed.

All functions are marked with pragma: no cover since this is test infrastructure.
"""

import logging
import os
from datetime import datetime
from typing import Optional


def initialise_logger(script_name: str, log_dir: str = 'logs', log_level: int = logging.INFO) -> logging.Logger:  # pragma: no cover
    """
    Initialize a logger with file and console handlers.

    Parameters:
    script_name (str): Name of the script (used for log file naming)
    log_dir (str): Directory to store log files
    log_level (int): Logging level (default: logging.INFO)

    Returns:
    logging.Logger: Configured logger instance
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(script_name)
    logger.setLevel(log_level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'{script_name}_{timestamp}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_info(logger: Optional[logging.Logger], message: str) -> None:  # pragma: no cover
    """
    Log an info message.

    Parameters:
    logger (logging.Logger): Logger instance
    message (str): Message to log
    """
    if logger:
        logger.info(message)
    else:
        print(f"INFO: {message}")


def log_error(logger: Optional[logging.Logger], message: str) -> None:  # pragma: no cover
    """
    Log an error message.

    Parameters:
    logger (logging.Logger): Logger instance
    message (str): Message to log
    """
    if logger:
        logger.error(message)
    else:
        print(f"ERROR: {message}")


def log_warning(logger: Optional[logging.Logger], message: str) -> None:  # pragma: no cover
    """
    Log a warning message.

    Parameters:
    logger (logging.Logger): Logger instance
    message (str): Message to log
    """
    if logger:
        logger.warning(message)
    else:
        print(f"WARNING: {message}")


def log_debug(logger: Optional[logging.Logger], message: str) -> None:  # pragma: no cover
    """
    Log a debug message.

    Parameters:
    logger (logging.Logger): Logger instance
    message (str): Message to log
    """
    if logger:
        logger.debug(message)
    else:
        print(f"DEBUG: {message}")
