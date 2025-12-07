"""
Logging Configuration and Utilities
File: backend/utils/logger.py
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        """Format log record with colors"""
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            # Add color to levelname
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logger(
    name: str = "hypatiax",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Setup and configure logger

    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for console only)
        max_bytes: Max bytes per log file before rotation
        backup_count: Number of backup files to keep
        use_colors: Use colored output for console

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    if use_colors:
        console_format = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(logging.DEBUG)

        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def get_request_logger(logger: logging.Logger):
    """
    Create a request logger decorator

    Args:
        logger: Base logger

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.info(f"Request started: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Request completed: {func.__name__} (duration={duration:.2f}s)")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"Request failed: {func.__name__} (duration={duration:.2f}s) - {str(e)}")
                raise

        return wrapper

    return decorator


class RequestLogger:
    """Context manager for request logging"""

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} (duration={duration:.2f}s)")
        else:
            self.logger.error(f"Failed: {self.operation} (duration={duration:.2f}s) - {exc_val}")

        return False  # Don't suppress exceptions


def log_function_call(logger: logging.Logger):
    """Decorator to log function calls"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise

        return wrapper

    return decorator


def create_timed_rotating_logger(
    name: str, log_file: str, when: str = "midnight", interval: int = 1, backup_count: int = 30
) -> logging.Logger:
    """
    Create logger with time-based rotation

    Args:
        name: Logger name
        log_file: Path to log file
        when: When to rotate (midnight, H, D, W0-W6)
        interval: Rotation interval
        backup_count: Number of backups to keep

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Timed rotating file handler
    handler = TimedRotatingFileHandler(log_file, when=when, interval=interval, backupCount=backup_count)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Pre-configured loggers for common use cases
def get_api_logger() -> logging.Logger:
    """Get logger for API requests"""
    return setup_logger(name="hypatiax.api", log_level=os.getenv("LOG_LEVEL", "INFO"), log_file="logs/api.log")


def get_service_logger(service_name: str) -> logging.Logger:
    """Get logger for a specific service"""
    return setup_logger(
        name=f"hypatiax.service.{service_name}",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=f"logs/{service_name}.log",
    )


def get_error_logger() -> logging.Logger:
    """Get logger for errors only"""
    return setup_logger(name="hypatiax.errors", log_level="ERROR", log_file="logs/errors.log")


# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = setup_logger(name="test_logger", log_level="DEBUG", log_file="logs/test.log")

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Test request logger
    with RequestLogger(logger, "test_operation"):
        import time

        time.sleep(0.1)
        logger.info("Doing some work...")

    print("\n✅ Logger test complete! Check logs/test.log")
