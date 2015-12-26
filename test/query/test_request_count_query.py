#!/usr/bin/env python

# standard library imports
from datetime import datetime

# third party related imports
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause
from elb_log_analyzer.query.request_count_query import RequestCountQuery


class TestQuery(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.rcq = RequestCountQuery(self.begin_at, self.end_at)

        self.mock_get_es()

    def mock_get_es(self):

        self.rcq.get_es = MagicMock()
        self.rcq.get_es.return_value = self.mock_es = MagicMock()
        self.mock_es.count.return_value = {'count': 1}

    def test_call(self):

        self.assertEqual(self.rcq.query(), 1)

        trc = TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at)
        self.mock_es.count.assert_called_with(
            index='logstash-2016.01.01',
            body={'filter': trc.get_clause()}
        )
