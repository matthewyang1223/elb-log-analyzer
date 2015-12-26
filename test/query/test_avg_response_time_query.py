#!/usr/bin/env python

# standard library imports
from datetime import datetime

# third party related imports
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause
from elb_log_analyzer.query.avg_response_time_query import AvgResponseTimeQuery


class TestQuery(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.artq = AvgResponseTimeQuery(self.begin_at, self.end_at)

        self.mock_get_es()

    def mock_get_es(self):

        self.artq.get_es = MagicMock()
        self.artq.get_es.return_value = self.mock_es = MagicMock()
        self.mock_es.search.return_value = {
            'aggregations': {'avg_resp_time':{'value': 1.0}}
        }

    def test_call(self):

        self.assertEqual(self.artq.query(), 1.0)

        trc = TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at)
        self.mock_es.search.assert_called_with(
            index='logstash-2016.01.01',
            body = {
                'filter': trc.get_clause(),
                'aggs': {
                    'avg_resp_time': {
                        'avg': {
                            'field': 'backend_processing_time'
                        }
                    }
                }
            }
        )
