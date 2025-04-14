"""
Logging Utility Module

This module provides a centralized logging configuration for the News Poster application.
It includes a custom formatter for colored log output.
"""

import logging
import sys
from typing import Optional

class CustomFormatter(logging.Formatter):
    """
    A custom formatter for logging messages with different colors based on log levels.

    Attributes:
        grey (str): ANSI escape sequence for grey color.
        yellow (str): ANSI escape sequence for yellow color.
        red (str): ANSI escape sequence for red color.
        bold_red (str): ANSI escape sequence for bold red color.
        reset (str): ANSI escape sequence to reset color.
        format (str): The log message format.
        FORMATS (dict): A dictionary mapping log levels to their respective log message formats.
    """
    grey = "\x1b[37;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    dark_grey = "\x1b[30;1m"
    reset = "\x1b[0m"
    format = '[%(levelname)s] %(asctime)s - %(name)s - %(message)s'

    FORMATS = {
        logging.DEBUG: dark_grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        """
        Formats the log record based on its log level.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log message.
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name (str): The name of the logger, typically __name__ from the calling module.
        level (int): The logging level to use. Defaults to logging.INFO.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # If the logger already has handlers, assume it's configured
    if logger.handlers:
        return logger
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter())
    
    # Add the handler to the logger
    logger.addHandler(console_handler)
    
    return logger

def setup_file_logging(filename: str = "news_poster.log", level: int = logging.INFO) -> None:
    """
    Set up file logging for the application.

    Args:
        filename (str): The name of the log file.
        level (int): The logging level to use. Defaults to logging.INFO.
    """
    # Configure root logger with file handler
    root_logger = logging.getLogger()
    
    # Create file handler which logs even debug messages
    file_handler = logging.FileHandler(filename, encoding='utf-8')
    file_handler.setLevel(level)
    
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    root_logger.addHandler(file_handler)
    
    # Log the start of the session
    root_logger.info("-------------- New logging session started --------------") 