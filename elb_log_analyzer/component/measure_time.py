#!/usr/bin/env python

# standard library imports
from timeit import default_timer as timer

# third party related imports

# local library imports
from elb_log_analyzer.logger import logger


def measure_time(func):

    def with_timer(*args, **kwargs):

        start = timer()
        ret = func(*args, **kwargs)
        end = timer()

        logger.debug(
            '%s(args=%s, kwargs=%s) takes %s',
            func.__name__,
            args,
            kwargs,
            end - start
        )

        return ret

    return with_timer
