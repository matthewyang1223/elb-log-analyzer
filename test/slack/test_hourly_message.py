#!/usr/bin/env python

# standard library imports
from datetime import datetime, timedelta

# third party related imports
from mock import patch
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.query.status_code_count_query import StatusCodeCountQuery
from elb_log_analyzer.slack.hourly_message import HourlyMessage


module = 'elb_log_analyzer.slack.hourly_message'


class TestGetMinutes(unittest.TestCase):

    def setUp(self):

        b = datetime.now()
        e = b + timedelta(seconds=1)
        self.hm = HourlyMessage(b, e)

    def test_call(self):

        self.assertEqual(self.hm.get_minutes(), 1)

class TestGetText(unittest.TestCase):

    def test_call(self):

        begin_at = datetime(2016, 1, 1)
        end_at = datetime(2016, 1, 1, 1)
        hm = HourlyMessage(begin_at, end_at)
        self.assertEqual(
            hm.get_text(),
            'Brief report [2016-01-01T00:00:00 ~ 2016-01-01T01:00:00]'
        )


class TestGetRequestCount(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)

    @patch(module + '.RequestCountQuery')
    def test_call(self, mock_req_count_query):

        mock_req_count_query.return_value.query.return_value = 1
        self.assertEqual(self.hm.get_request_count(), 1)
        mock_req_count_query.assert_called_with(self.begin_at, self.end_at)


class TestGetAvgResponseTime(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)

    @patch(module + '.AvgResponseTimeQuery')
    def test_call(self, mock_avg_resp_time_query):

        mock_avg_resp_time_query.return_value.query.return_value = 1
        self.assertEqual(self.hm.get_avg_response_time(), 1)
        mock_avg_resp_time_query.assert_called_with(self.begin_at, self.end_at)



class TestGetApdex(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)

    @patch(module + '.ApdexQuery')
    def test_call(self, mock_apdex_query):

        mock_apdex_query.return_value.query.return_value = 1
        self.assertEqual(self.hm.get_apdex(), 1)
        mock_apdex_query.assert_called_with(
            self.begin_at,
            self.end_at,
            HourlyMessage.APDEX_THRESHOLD
        )


class TestGetHttpStatusCodeCount(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)

    @patch(module + '.StatusCodeCountQuery')
    def test_call(self, mock_status_code_count_query):

        mock_status_code_count_query.return_value.query.return_value = 1
        self.assertEqual(self.hm.get_http_status_code_count(200), 1)
        mock_status_code_count_query.assert_called_with(
            self.begin_at,
            self.end_at,
            200
        )


class TestMakeApdexReport(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)
        self.mock_get_request_count()
        self.mock_get_avg_response_time()
        self.mock_get_apdex()

    def mock_get_request_count(self):

        self.hm.get_request_count = MagicMock(return_value=100)

    def mock_get_avg_response_time(self):

        self.hm.get_avg_response_time = MagicMock(return_value=0.1)

    def mock_get_apdex(self):

        self.hm.get_apdex = MagicMock(return_value=0.75)

    def test_call(self):

        self.assertEqual(
            self.hm.make_apdex_report(),
            {
                'color': '#ff0000',
                'title': 'Server summary',
                'fields': [
                    dict(title='Req count', value=100, short=True),
                    dict(title='Avg resp time', value='100.00 ms', short=True),
                    dict(title='Throughput', value='1.67 rpm', short=True),
                    dict(title='Apdex (0.05)', value='0.75', short=True)
                ]
            }
        )


class TestMakeStatusCodeReport(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)
        self.mock_get_http_status_code_count()

    def mock_get_http_status_code_count(self):

        def side_effect(s):

            if s == StatusCodeCountQuery.SUCCESS:
                return 4
            elif s == StatusCodeCountQuery.REDIRECTION:
                return 3
            elif s == StatusCodeCountQuery.CLIENT_ERROR:
                return 2

            return 1

        self.hm.get_http_status_code_count = MagicMock(side_effect=side_effect)

    def test_call(self):

        self.assertEqual(
            self.hm.make_status_code_report(),
            {
                'color': '#fbb034',
                'title': 'HTTP summary',
                'fields': [
                    dict(title='2XX', value=4, short=True),
                    dict(title='3XX', value=3, short=True),
                    dict(title='4XX', value=2, short=True),
                    dict(title='5XX', value=1, short=True)
                ]
            }
        )


class TestGetAttachments(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.hm = HourlyMessage(self.begin_at, self.end_at)

    def test_call(self):

        self.hm.make_apdex_report = MagicMock(return_value=1)
        self.hm.make_status_code_report = MagicMock(return_value=2)
        self.assertEqual(self.hm.get_attachments(), [1, 2])
