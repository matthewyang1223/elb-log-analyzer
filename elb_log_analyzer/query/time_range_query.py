#!/usr/bin/env python

# stadard library imports
from calendar import timegm

# third party related imports

# local library imports


class TimeRangeQuery(object):

    def __init__(self, field='timestamp', begin_time=None, end_time=None):

        if begin_time is None and end_time is None:
            raise ValueError('Not a valid query')

        self.field = field
        self.begin_time = begin_time
        self.end_time = end_time

    def get_clause(self):

        ret = {'range': {self.field: {}}}
        obj = ret['range'][self.field]

        if self.begin_time is not None:
            obj['gte'] = timegm(self.begin_time.timetuple()) * 1000

        if self.end_time is not None:
            obj['lt'] = timegm(self.end_time.timetuple()) * 1000

        return ret