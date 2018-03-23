#!/usr/bin/env python

# standard library imports
import logging
import logging.config

# third party related imports

# local library imports
from elb_log_analyzer.config import config_file


__all__ = ['logger']

logging.config.fileConfig(config_file)
logger = logging.getLogger('elb-log-analyzer')
