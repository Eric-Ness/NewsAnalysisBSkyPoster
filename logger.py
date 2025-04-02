# This module contains a custom formatter for logging messages with different log levels.
import logging

class CustomFormatter(logging.Formatter):
    """
    A custom formatter for logging messages with different log levels.

    Attributes:
        grey (str): ANSI escape sequence for grey color.
        yellow (str): ANSI escape sequence for yellow color.
        red (str): ANSI escape sequence for red color.
        bold_red (str): ANSI escape sequence for bold red color.
        reset (str): ANSI escape sequence to reset color.
        format (str): The log message format.
        FORMATS (dict): A dictionary mapping log levels to their respective log message formats.

    Methods:
        format(record): Formats the log record based on its log level.

    Usage:
        formatter = CustomFormatter()
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    """
    grey = "\x1b[37;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    dark_grey = "\x1b[30;1m"
    reset = "\x1b[0m"
    format = '[%(levelname)s] %(asctime)s - %(message)s'

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
    
# create logger
global log
log = logging.getLogger("rss")
log.setLevel(logging.INFO)
log.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
log.addHandler(ch)