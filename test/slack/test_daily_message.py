#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# standard library imports
from datetime import date

# third party related imports
from mock import patch
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.slack.daily_message import ApiStat, DailyMessage, DAY


module = 'elb_log_analyzer.slack.daily_message'


class TestGetText(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def test(self):

        self.assertEqual(self.dm.get_text(), 'Daily report [2016-01-01]')


class TestMakePopularApiReport(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def mock_query(self, mock_query_cls):

        mock_query_cls.return_value.query.return_value = [
            {
                'key': 'api1',
                'stats': {
                    'count': 100,
                    'min': 0.1,
                    'max': 1.0,
                    'avg': 0.5,
                    'std_deviation': 0.25
                }
            },
            {
                'key': 'api2',
                'stats': {
                    'count': 1000,
                    'min': 1.0,
                    'max': 10.0,
                    'avg': 5.0,
                    'std_deviation': 2.5
                }
            }
        ]

    @patch(module + '.ApiExtendedStatQuery')
    def test(self, mock_query_cls):

        self.mock_query(mock_query_cls)

        self.assertEqual(
            self.dm.make_popular_api_report(),
            {
                'color': '#ffdd00',
                'title': 'Top 10 popular API',
                'fields': [
                    {
                        'title': 'api1',
                        'short': False,
                        'value': (
                            'count: 100, '
                            'min: 100.00 ms, '
                            'max: 1000.00 ms, '
                            'μ: 500.00 ms, '
                            'σ: 250.00 ms'
                        )
                    },
                    {
                        'title': 'api2',
                        'short': False,
                        'value': (
                            'count: 1000, '
                            'min: 1000.00 ms, '
                            'max: 10000.00 ms, '
                            'μ: 5000.00 ms, '
                            'σ: 2500.00 ms'
                        )
                    }
                ]
            }
        )
        mock_query_cls.assert_called_with(
            self.d, self.d + DAY, 'count', False, 10
        )
        mock_query_cls.return_value.query.assert_called_with()


class TestMakeSlowestApiReport(TestMakePopularApiReport):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    @patch(module + '.ApiExtendedStatQuery')
    def test(self, mock_query_cls):

        self.mock_query(mock_query_cls)
        self.assertEqual(
            self.dm.make_slowest_api_report(),
            {
                'color': '#c1d82f',
                'title': 'Top 10 slowest API',
                'fields': [
                    {
                        'title': 'api1',
                        'short': False,
                        'value': (
                            'count: 100, '
                            'min: 100.00 ms, '
                            'max: 1000.00 ms, '
                            'μ: 500.00 ms, '
                            'σ: 250.00 ms'
                        )
                    },
                    {
                        'title': 'api2',
                        'short': False,
                        'value': (
                            'count: 1000, '
                            'min: 1000.00 ms, '
                            'max: 10000.00 ms, '
                            'μ: 5000.00 ms, '
                            'σ: 2500.00 ms'
                        )
                    },
                ]
            }
        )
        mock_query_cls.assert_called_with(
            self.d, self.d + DAY, 'avg', False, 10
        )
        mock_query_cls.return_value.query.assert_called_with()


class TestGetAttachments(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def test(self):

        self.dm.make_apdex_report = MagicMock(return_value=1)
        self.dm.make_status_code_report = MagicMock(return_value=2)
        self.dm.make_popular_api_report = MagicMock(return_value=3)
        self.dm.make_slowest_api_report = MagicMock(return_value=4)
        self.assertEqual(self.dm.get_attachments(), [1, 2, 3, 4])
