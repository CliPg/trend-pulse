"""
Unified logging configuration for TrendPulse.
Provides colored console output and file logging with rotation.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # Color mappings for different log levels
    LOG_COLORS = {
        logging.DEBUG: Colors.BRIGHT_BLUE,
        logging.INFO: Colors.BRIGHT_GREEN,
        logging.WARNING: Colors.BRIGHT_YELLOW,
        logging.ERROR: Colors.BRIGHT_RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD,
    }

    # Icons for different log levels
    LOG_ICONS = {
        logging.DEBUG: "",
        logging.INFO: "",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "⛔",
    }

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None, use_colors: bool = True):
        """
        Initialize colored formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
            use_colors: Whether to use colors (disable for file output)
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and icons."""
        # Add icon to message if using colors
        if self.use_colors:
            icon = self.LOG_ICONS.get(record.levelno, "")
            if icon:
                record.msg = f"{icon} {record.msg}"

        # Format the message
        result = super().format(record)

        # Add color if enabled
        if self.use_colors:
            level_color = self.LOG_COLORS.get(record.levelno, "")
            result = f"{level_color}{result}{Colors.RESET}"

        return result


def setup_logger(
    name: str = "trendpulse",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up a logger with colored console output and optional file logging.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Path to log file (if None, uses default location)
        console_output: Whether to output to console
        max_file_size: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger("my_module")
        >>> logger.info("Hello, world!")
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Prevent propagation to root logger
    logger.propagate = False

    # Define log format
    # Format: [2025-01-16 14:30:45] [INFO] [module_name] Message
    log_format = "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Console handler with colors
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        colored_formatter = ColoredFormatter(log_format, date_format, use_colors=True)
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)

    # File handler (no colors)
    if log_file is not None:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_formatter = ColoredFormatter(log_format, date_format, use_colors=False)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger for a module.

    This is a convenience function that uses the default logging configuration.
    For custom configuration, use setup_logger() directly.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance

    Example:
        >>> from src.utils.logger_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    # Default log file location
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_file = log_dir / f"trendpulse_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)

    # Only setup if not already configured
    if not logger.handlers:
        logger = setup_logger(
            name=name,
            level=logging.INFO,
            log_file=str(log_file),
            console_output=True,
        )

    return logger


# Convenience function for different modules
def get_collector_logger(platform: str) -> logging.Logger:
    """
    Get logger for data collectors.

    Args:
        platform: Platform name (reddit, youtube, twitter)

    Returns:
        Logger instance
    """
    return get_logger(f"trendpulse.collector.{platform}")


def get_ai_logger() -> logging.Logger:
    """Get logger for AI analysis module."""
    return get_logger("trendpulse.ai_analysis")


def get_api_logger() -> logging.Logger:
    """Get logger for API module."""
    return get_logger("trendpulse.api")


def get_db_logger() -> logging.Logger:
    """Get logger for database module."""
    return get_logger("trendpulse.database")


def get_orchestrator_logger() -> logging.Logger:
    """Get logger for orchestrator module."""
    return get_logger("trendpulse.orchestrator")


# Pre-configured loggers for quick access
logger = get_logger("trendpulse")
collector_logger = get_logger("trendpulse.collector")
ai_logger = get_ai_logger()
api_logger = get_api_logger()
db_logger = get_db_logger()
orchestrator_logger = get_orchestrator_logger()
