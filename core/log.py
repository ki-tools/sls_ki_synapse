import logging
from .param_store import ParamStore

"""
Setup the logger.
"""
logging.basicConfig(level=logging.getLevelName(ParamStore.LOG_LEVEL(default='INFO')))
