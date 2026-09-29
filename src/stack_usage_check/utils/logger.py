import json
import logging
import os

from pathlib import Path


class Config(object):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    _CONFIG_FILE: Path = Path(os.path.join(__location__, "config.json"))
    _CONFIG: dict = None

    def __init__(self, config_file: Path = None) -> None:
        config_file = Config._CONFIG_FILE
        with open(config_file, "r") as f:
            Config._CONFIG = json.load(f)

    @staticmethod
    def get_config() -> dict:
        return Config._CONFIG


def configure_logger(log_level: str):
    """
    Configure logger with a stream handler and a formatter
    that shows the module name, log level, and message content.
    Before configuring the logger handler, all preexisting log handlers
    are removed before creating a new stream handler of which to tie the new
    root logger handler to.

    Args:
        log_level (str): The chosen log level from the command line arguments.
    """
    logger = logging.getLogger()
    log_level = getattr(logging, log_level.upper())
    logger.setLevel(log_level)
    # Delete logger handlers if exist
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    fmt = "%(levelname)s: %(filename)s - line %(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
