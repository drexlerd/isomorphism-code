import logging
import sys

formatter = logging.Formatter('%(asctime)s - %(message)s')


def initialize_logger(name: str):
    return logging.getLogger(name)


def add_console_handler(logger: logging.Logger):
    global formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def remove_console_handler(logger: logging.Logger, console_handler: logging.StreamHandler):
    logger.removeHandler(console_handler)

