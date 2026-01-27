"""
User-friendly logging system with colorful console output and file logging.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Try to set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        # Try to set console to UTF-8
        os.system('chcp 65001 > nul 2>&1')
        # Reconfigure stdout with UTF-8 encoding
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Detect if console supports Unicode
def supports_unicode():
    """Check if the console supports Unicode characters."""
    try:
        # Try to encode a test emoji
        '✓'.encode(sys.stdout.encoding or 'ascii')
        return True
    except (UnicodeEncodeError, AttributeError):
        return False

USE_UNICODE = supports_unicode()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    # Unicode icons (for UTF-8 consoles)
    ICONS_UNICODE = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠',
        'ERROR': '✗',
        'CRITICAL': '🔥',
    }

    # ASCII fallback icons (for non-UTF-8 consoles)
    ICONS_ASCII = {
        'DEBUG': '[D]',
        'INFO': '[+]',
        'WARNING': '[!]',
        'ERROR': '[X]',
        'CRITICAL': '[!!]',
    }

    def __init__(self):
        super().__init__()
        # Choose icon set based on console capability
        self.ICONS = self.ICONS_UNICODE if USE_UNICODE else self.ICONS_ASCII

    def format(self, record):
        """Format log record with colors and icons."""
        # Add color to level name
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        icon = self.ICONS.get(levelname, '')

        # Format: [TIME] [LEVEL] [ICON] Message
        log_time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        message = record.getMessage()

        # Format with color and icon for console
        try:
            return f"{color}[{log_time}] [{levelname}] {icon} {message}{Style.RESET_ALL}"
        except UnicodeEncodeError:
            # Fallback to ASCII if encoding fails
            return f"{color}[{log_time}] [{levelname}] {message}{Style.RESET_ALL}"


class SimpleFormatter(logging.Formatter):
    """Simple formatter without timestamps for clean console output."""

    def format(self, record):
        return record.getMessage()


def setup_logger(name: str = "price_monitor", log_level: str = "INFO") -> logging.Logger:
    """
    Set up a user-friendly logger with both console and file output.

    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with detailed logs
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"price_monitor_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "price_monitor") -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)

    return logger


# Convenience functions for cleaner code
def info(message: str):
    """Log info message."""
    get_logger().info(message)


def success(message: str):
    """Log success message (info level with custom formatting)."""
    icon = "✓" if USE_UNICODE else "[+]"
    get_logger().info(f"{icon} {message}")


def warning(message: str):
    """Log warning message."""
    get_logger().warning(message)


def error(message: str):
    """Log error message."""
    get_logger().error(message)


def debug(message: str):
    """Log debug message."""
    get_logger().debug(message)


def critical(message: str):
    """Log critical message."""
    get_logger().critical(message)
