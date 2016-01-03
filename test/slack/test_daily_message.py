#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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


class TestMakePopularApiReport(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def test(self):

        self.dm.get_api_extended_stats = MagicMock(return_value=[
            ApiStat('api1', 100, 0.1, 1.0, 0.5, 0.25),
            ApiStat('api2', 1000, 1.0, 10.0, 5.0, 2.5)
        ])
        self.assertEqual(
            self.dm.make_popular_api_report(),
            {
                'color': '#ffdd00',
                'title': 'Top 10 popular API',
                'fields': [
                    {
                        'title': 'api2',
                        'short': True,
                        'value': (
                            '• count: 1000\n'
                            '• min: 1000.00 ms\n'
                            '• max: 10000.00 ms\n'
                            '• μ: 5000.00 ms\n'
                            '• σ: 2500.00 ms'
                        )
                    },
                    {
                        'title': 'api1',
                        'short': True,
                        'value': (
                            '• count: 100\n'
                            '• min: 100.00 ms\n'
                            '• max: 1000.00 ms\n'
                            '• μ: 500.00 ms\n'
                            '• σ: 250.00 ms'
                        )
                    }
                ]
            }
        )


class TestMakeSlowestApiReport(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def test(self):

        self.dm.get_api_extended_stats = MagicMock(return_value=[
            ApiStat('api1', 100, 0.1, 1.0, 0.5, 0.25),
            ApiStat('api2', 1000, 1.0, 10.0, 5.0, 2.5)
        ])
        self.assertEqual(
            self.dm.make_slowest_api_report(),
            {
                'color': '#c1d82f',
                'title': 'Top 10 slowest API',
                'fields': [
                    {
                        'title': 'api2',
                        'short': True,
                        'value': (
                            '• count: 1000\n'
                            '• min: 1000.00 ms\n'
                            '• max: 10000.00 ms\n'
                            '• μ: 5000.00 ms\n'
                            '• σ: 2500.00 ms'
                        )
                    },
                    {
                        'title': 'api1',
                        'short': True,
                        'value': (
                            '• count: 100\n'
                            '• min: 100.00 ms\n'
                            '• max: 1000.00 ms\n'
                            '• μ: 500.00 ms\n'
                            '• σ: 250.00 ms'
                        )
                    }
                ]
            }
        )
