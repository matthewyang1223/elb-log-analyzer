#!/usr/bin/env python

# standard library imports
from datetime import datetime

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.slack.hourly_message import HourlyMessage


class TestGetIndexName(unittest.TestCase):

    def test_when_begin_at_and_end_at_on_the_same_day(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 1, 12)
        hm = HourlyMessage(begin_at, end_at)
        self.assertEqual(hm.get_index_name(), 'logstash-2016.01.01')

    def test_when_begin_at_and_end_at_not_on_the_same_day(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 2)
        hm = HourlyMessage(begin_at, end_at)
        self.assertEqual(
            hm.get_index_name(),
            'logstash-2016.01.01,logstash-2016.01.02'
        )


class TestGetText(unittest.TestCase):

    def test_call(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 1, 1)
        hm = HourlyMessage(begin_at, end_at)
        self.assertEqual(
            hm.get_text(),
            'Brief report [2016-01-01T00:00:00 ~ 2016-01-01T01:00:00]'
        )
