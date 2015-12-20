#!/usr/bin/env python

# standard library imports
from datetime import timedelta

# third party related imports

# local library imports
from elb_log_analyzer.query.base_query import BaseQuery


class BaseTimeRangeQuery(BaseQuery):

    def __init__(self, begin_at, end_at):

        super(BaseTimeRangeQuery, self).__init__()
        self.begin_at = begin_at
        self.end_at = end_at

    def get_index_name(self):

        d = self.begin_at.date()
        e = self.end_at.date()
        day = timedelta(days=1)
        span = []

        while d <= e:
            span.append(d)
            d += day

        return ','.join(['logstash-' + s.strftime('%Y.%m.%d') for s in span])
