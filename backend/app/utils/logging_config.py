"""
Logging Configuration

Provides centralized logging configuration for the application.
"""

import logging
import sys
from typing import Optional

# Default log format
DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Color codes for terminal output (optional enhancement)
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log output in terminal."""

    def format(self, record: logging.LogRecord) -> str:
        # Save original levelname
        original_levelname = record.levelname

        # Add color if running in terminal
        if sys.stdout.isatty():
            color = COLORS.get(record.levelname, COLORS["RESET"])
            record.levelname = f"{color}{record.levelname}{COLORS['RESET']}"

        result = super().format(record)

        # Restore original levelname
        record.levelname = original_levelname

        return result


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure root logging for the application.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        use_colors: Whether to use colored output (default: True)

    Returns:
        Configured root logger
    """
    log_format = format_string or DEFAULT_FORMAT

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(log_format, datefmt=DATE_FORMAT)
    else:
        formatter = logging.Formatter(log_format, datefmt=DATE_FORMAT)

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Application-specific loggers
class AppLogger:
    """Convenience class for application logging."""

    def __init__(self, name: str):
        self.logger = get_logger(name)

    def debug(self, message: str, **extra):
        """Log debug message."""
        self.logger.debug(message, extra=extra)

    def info(self, message: str, **extra):
        """Log info message."""
        self.logger.info(message, extra=extra)

    def warning(self, message: str, **extra):
        """Log warning message."""
        self.logger.warning(message, extra=extra)

    def error(self, message: str, **extra):
        """Log error message."""
        self.logger.error(message, extra=extra)

    def critical(self, message: str, **extra):
        """Log critical message."""
        self.logger.critical(message, extra=extra)

    def exception(self, message: str, **extra):
        """Log exception with traceback."""
        self.logger.exception(message, extra=extra)


# Pre-configured loggers for common modules
def get_db_logger() -> AppLogger:
    """Get logger for database operations."""
    return AppLogger("campus_to_hire.database")


def get_api_logger() -> AppLogger:
    """Get logger for API operations."""
    return AppLogger("campus_to_hire.api")


def get_ai_logger() -> AppLogger:
    """Get logger for AI/Bedrock operations."""
    return AppLogger("campus_to_hire.ai")


def get_auth_logger() -> AppLogger:
    """Get logger for authentication operations."""
    return AppLogger("campus_to_hire.auth")


# Initialize logging on module import
# This ensures logging is configured when the module is first imported
setup_logging()
