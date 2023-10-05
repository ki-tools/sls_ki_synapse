import logging
from .env import Env

"""
Setup the logger.
"""
logger = logging.getLogger()

if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logging.basicConfig(level=logging.getLevelName(Env.LOG_LEVEL(default='INFO')))
