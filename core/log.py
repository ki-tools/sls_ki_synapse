import os
import logging
from core.param_store import ParamStore

"""
Setup the logger.
"""
logging.basicConfig(level=logging.getLevelName(ParamStore.LOG_LEVEL(default='INFO')))
