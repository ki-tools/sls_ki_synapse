import logging
from .app_env import AppEnv

"""
Setup the logger.
"""
logger = logging.getLogger()

if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logging.basicConfig(level=logging.getLevelName(AppEnv.LOG_LEVEL(default='INFO')))
