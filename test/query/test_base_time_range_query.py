#!/usr/bin/env python

# standard library imports
from datetime import datetime

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.query.base_time_range_query import BaseTimeRangeQuery


class TestGetIndexName(unittest.TestCase):

    def test_when_begin_at_and_end_at_on_the_same_day(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 1, 12)
        btrq = BaseTimeRangeQuery(begin_at, end_at)
        self.assertEqual(btrq.get_index_name(), 'logstash-2016.01.01')

    def test_when_end_at_is_beginning_of_a_day(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 2)
        btrq = BaseTimeRangeQuery(begin_at, end_at)
        self.assertEqual(btrq.get_index_name(), 'logstash-2016.01.01')

    def test_when_begin_at_and_end_at_not_on_the_same_day(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 2, 1)
        btrq = BaseTimeRangeQuery(begin_at, end_at)
        self.assertEqual(
            btrq.get_index_name(),
            'logstash-2016.01.01,logstash-2016.01.02'
        )
