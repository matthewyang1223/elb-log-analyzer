#!/usr/bin/env python

# standard library imports
from random import choice, randrange
from datetime import datetime

# third party related imports
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.query.api_extended_stat_query import (
    ApiExtendedStatQuery
)


class TestQuery(unittest.TestCase):

    def setUp(self):

        self.begin_at = datetime(2016, 1, 1)
        self.end_at = datetime(2016, 1, 1, 1)
        self.order_by = choice(['count', 'min', 'max', 'avg', 'sum'])
        self.asc = choice([True, False])
        self.limit = randrange(1, 100)
        self.aesq = ApiExtendedStatQuery(
            self.begin_at,
            self.end_at,
            self.order_by,
            self.asc,
            self.limit
        )
        self.mock_get_es()

    def mock_get_es(self):

        self.mock_es = MagicMock()
        self.aesq.get_es = MagicMock(return_value=self.mock_es)
        self.query_result = [
            {
                'key': 'ctrl#action',
                'doc_count': 100,
                'stats': {
                    'count': 100,
                    'min': 1,
                    'max': 10,
                    'avg': 5,
                    'sum': 1000,
                    'sum_of_squares': 10000,
                    'variance': 4,
                    'std_deviation': 2,
                    'std_deviation_bounds': {'upper': 10, 'lower': 0}
                }
            }
        ]
        self.mock_es.search.return_value = {
            'aggregations': {'apis': {'buckets': self.query_result}}
        }

    def test(self):

        self.assertEqual(self.aesq.query(), self.query_result)
        self.mock_es.search.assert_called_with(
            index='logstash-2016.01.01',
            body={
                'query': {
                    'bool': {
                        'filter': [
                            {
                                'range': {
                                    'timestamp': {
                                        'gte': 1451606400000,
                                        'lt': 1451610000000
                                    }
                                }
                            },
                            {'exists': {'field': 'rails.controller#action'}},
                            {'term': {'domain_name': 'api.thekono.com'}},
                            {'range': {'backend_processing_time': {'gte': 0}}}
                        ]
                    }
                },
                'size': 0,
                'aggs': {
                    'apis': {
                        'terms': {
                            'field': 'rails.controller#action.keyword',
                            'order': {
                                'stats.' + self.order_by:
                                'asc' if self.asc else 'desc'
                            },
                            'size': self.limit
                        },
                        'aggs': {
                            'stats': {
                                'extended_stats': {
                                    'field': 'backend_processing_time'
                                }
                            }
                        }
                    }
                }
            }
        )
