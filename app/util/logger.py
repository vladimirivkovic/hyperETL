import logging
import time
import sys

LOG_FILE = f'log/app-{time.time()}.log'
LOG_FORMAT = '%(name)s - %(levelname)s - %(message)s'


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # handler = logging.FileHandler(LOG_FILE)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger
