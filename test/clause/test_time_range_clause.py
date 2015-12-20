#!/usr/bin/env python

# stadard library imports
from calendar import timegm
from datetime import datetime, timedelta

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause


class TestGetClause(unittest.TestCase):

    def test_when_only_begin_time(self):

        now = datetime.utcnow()
        trc = TimeRangeClause(begin_time=now)
        self.assertEqual(
            trc.get_clause(),
            {
                'range': {'timestamp': {'gte': timegm(now.timetuple()) * 1000}}
            }
        )

    def test_when_only_end_time(self):

        now = datetime.utcnow()
        trc = TimeRangeClause(end_time=now)
        self.assertEqual(
            trc.get_clause(),
            {
                'range': {'timestamp': {'lt': timegm(now.timetuple()) * 1000}}
            }
        )

    def test_when_begin_time_and_end_time(self):

        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        trc = TimeRangeClause(begin_time=one_hour_ago, end_time=now)
        self.assertEqual(
            trc.get_clause(),
            {
                'range': {
                    'timestamp': {
                        'gte': timegm(one_hour_ago.timetuple()) * 1000,
                        'lt': timegm(now.timetuple()) * 1000
                    }
                }
            }
        )
