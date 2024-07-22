"""
Provides logging functions.
"""

import logging
import logging.config


def _get_root_logger() -> logging.Logger:
    return logging.getLogger()


def config_logger():
    logger = _get_root_logger()
    logging.basicConfig(filename='phenoplier.log', filemode='a', level=logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)


def print_and_log(message: str, log_message, verbose: bool, level: int = logging.INFO, logger: logging.Logger = None):
    """
    Prints and logs a message.

    :param message: message to print and log.
    :param log_message: message to log. Used if message contains rich text formatting.
    :param verbose: if True, and the level is DEBUG, the message is printed to stdout.
    :param level: logging level.
    :param logger: logger instance.
    """
    if logger is None:
        logger = _get_root_logger()

    logger.log(level, message)
    print(message)


def print_and_log_error(message: str, logger: logging.Logger = None):
    """
    Prints and logs an error message.

    :param message: message to print and log.
    :param logger: logger instance.
    """
    print_and_log(message, verbose=False, level=logging.ERROR, logger=logger)

