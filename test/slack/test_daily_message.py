#!/usr/bin/env python

# standard library imports
from datetime import date

# third party related imports
from mock import patch
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.slack.daily_message import ApiStat, DailyMessage


module = 'elb_log_analyzer.slack.daily_message'


class TestGetText(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def test(self):

        self.assertEqual(self.dm.get_text(), 'Daily report [2016-01-01]')


class TestGetApiExtendedStats(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    @patch(module + '.ApiExtendedStatQuery')
    def test(self, mock_query_cls):

        mock_query_cls.return_value = mock_query_instance = MagicMock()
        mock_query_instance.query.return_value = [
            {
                "key": "ctrl#action",
                "doc_count": 100,
                "stats": {
                    "count": 100,
                    "min": 0.,
                    "max": 10.,
                    "avg": 0.1,
                    "sum": 10000.,
                    "sum_of_squares": 11724.0,
                    "variance": 1.0,
                    "std_deviation": 0.25,
                    "std_deviation_bounds": {
                        "upper": 0.5,
                        "lower": 0,
                    }
                }
            }
        ]

        self.assertEqual(
            self.dm.get_api_extended_stats(),
            [ApiStat('ctrl#action', 100, 0., 10., 0.1, 0.25)]
        )
