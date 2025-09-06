"""
Logging module for AI Agent Framework with colored output and rich formatting.
Provides structured logging with timestamps, module paths, line numbers, and color coding.
"""

import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from rich.theme import Theme

"""
AI代理框架的日志模块，提供彩色输出和丰富格式。
提供结构化日志记录，包含时间戳、模块路径、行号和颜色编码。
"""


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output based on log level."""

    COLORS = {
        "DEBUG": "blue",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
    }

    def format(self, record):
        # Get the original formatted message
        message = super().format(record)

        # Create colored text based on log level
        level_color = self.COLORS.get(record.levelname, "white")
        colored_message = Text(message, style=level_color)

        return colored_message


def setup_logging(config: Optional[dict] = None) -> logging.Logger:
    """
    Set up logging configuration based on provided config.

    Args:
        config: Dictionary containing logging configuration

    Returns:
        Configured logger instance
    """
    if config is None:
        config = {"level": "INFO", "file": "logs/ai_agent.log", "console_output": True}

    # Create logs directory if it doesn't exist
    log_file = Path(config.get("file", "logs/ai_agent.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Set up rich console for colored output
    console = Console(
        theme=Theme(
            {
                "logging.level.debug": "blue",
                "logging.level.info": "green",
                "logging.level.warning": "yellow",
                "logging.level.error": "red",
                "logging.level.critical": "bold red",
            }
        )
    )

    # Create root logger
    logger = logging.getLogger("ai_agent")

    # Set log level
    log_level = getattr(logging, config.get("level", "DEBUG").upper())
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler for persistent logging
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    # Console handler with rich formatting
    if config.get("console_output", True):
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=True,
            level=log_level,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
        )
        console_handler.setFormatter(
            logging.Formatter("%(message)s", datefmt="%H:%M:%S")
        )
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.

    Args:
        name: Name of the module (usually __name__)

    Returns:
        Logger instance configured for the module
    """
    return logging.getLogger(f"ai_agent.{name}")


# Global logger instance
logger = get_logger(__name__)
