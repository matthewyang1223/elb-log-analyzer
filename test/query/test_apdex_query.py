#!/usr/bin/env python

# standard library imports
from datetime import datetime

# third party related imports
from mock import patch
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.query.apdex_query import ApdexQuery


module = 'elb_log_analyzer.query.apdex_query'


class TestGetSatisfiedRequestCount(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.aq = ApdexQuery(self.begin_at, self.end_at, 0.1)

    def mock_get_es(self):

        self.aq.get_es = MagicMock()
        return self.aq.get_es.return_value

    def test_call(self):

        mock_es = self.mock_get_es()
        mock_es.count.return_value = {'count': 100}

        self.assertEqual(self.aq.get_satisfied_request_count(), 100)
        mock_es.count.assert_called_with(
            index='logstash-2016.01.01',
            body={
                'query': {
                    'bool': {
                        'filter': [
                            {
                                'range': {
                                    'timestamp': {
                                        'gte': 1451606400000,
                                        'lt': 1451692800000
                                    }
                                }
                            },
                            {'exists': {'field': 'rails.controller#action'}},
                            {'term': {'domain_name': 'api.thekono.com'}},
                            {
                                'range': {
                                    'backend_processing_time': {
                                        'gte': 0, 'lt': 0.1
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )


class TestGetToleratingRequestCount(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.aq = ApdexQuery(self.begin_at, self.end_at, 0.1)

    def mock_get_es(self):

        self.aq.get_es = MagicMock()
        return self.aq.get_es.return_value

    def test_call(self):

        mock_es = self.mock_get_es()
        mock_es.count.return_value = {'count': 100}

        self.assertEqual(self.aq.get_tolerating_request_count(), 100)
        mock_es.count.assert_called_with(
            index='logstash-2016.01.01',
            body={
                'query': {
                    'bool': {
                        'filter': [
                            {
                                'range': {
                                    'timestamp': {
                                        'gte': 1451606400000,
                                        'lt': 1451692800000
                                    }
                                }
                            },
                            {'exists': {'field': 'rails.controller#action'}},
                            {'term': {'domain_name': 'api.thekono.com'}},
                            {
                                'range': {
                                    'backend_processing_time': {
                                        'gte': 0.1, 'lt': 0.4
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )


class TestGetRequestCount(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.aq = ApdexQuery(self.begin_at, self.end_at, 0.1)

    @patch(module + '.RequestCountQuery')
    def test_call(self, mock_req_cnt_query):

        mock_req_cnt_query.return_value.query.return_value = 100
        self.assertEqual(self.aq.get_request_count(), 100)
        mock_req_cnt_query.assert_called_with(self.begin_at, self.end_at)


class TestQuery(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 2)
        self.aq = ApdexQuery(self.begin_at, self.end_at, 0.1)

    def test_call(self):

        self.aq.get_satisfied_request_count = MagicMock(return_value=1)
        self.aq.get_tolerating_request_count = MagicMock(return_value=2)
        self.aq.get_request_count = MagicMock(return_value=3)
        self.assertAlmostEqual(self.aq.query(), (1 + 1) / 3.0)
