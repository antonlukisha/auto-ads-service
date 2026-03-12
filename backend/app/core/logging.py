import logging
import sys


class Color:
    RESET = "\033[0m"
    DEBUG = "\033[36m"
    INFO = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"
    CRITICAL = "\033[1m\033[31m"


class ColorFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record with color based on the log level.

        :param record: The log record to format.
        :type record: logging.LogRecord
        :return: The formatted log record.
        :rtype: str
        """
        orig_levelname = record.levelname

        color = getattr(Color, record.levelname, Color.RESET)
        record.levelname = f"{color}{record.levelname}{Color.RESET}"

        msg = super().format(record)

        record.levelname = orig_levelname

        return msg


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration with optional file logging.

    :param level: The logging level (DEBUG, INFO, WARNING, ERROR).
    :type level: str
    :return: nothing
    :rtype: None
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    log_level = level_map.get(level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = ColorFormatter(log_format, date_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)


logger = logging.getLogger("backend")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    :param name: The name of the logger.
    :type name: str
    :return: The logger instance.
    :rtype: logging.Logger
    """
    return logging.getLogger(f"backend.{name}")


def get_uvicorn_logger_config() -> dict:
    """
    Get logging configuration for Uvicorn with colored output

    :return: Logging configuration dictionary
    :rtype: dict
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "app.core.logging.ColorFormatter",
                "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "app": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
        "root": {"level": "INFO", "handlers": ["default"]},
    }
