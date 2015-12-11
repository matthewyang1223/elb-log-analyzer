#!/usr/bin/env python

# stadard library imports

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.query.range_query import RangeQuery


class TestGetClause(unittest.TestCase):

    def test_when_only_min_val(self):

        rq = RangeQuery('a_field', min_val=1)
        self.assertEqual(
            rq.get_clause(),
            {'range': {'a_field': {'gte': 1}}}
        )

    def test_when_only_max_val(self):

        rq = RangeQuery('a_field', max_val=10)
        self.assertEqual(
            rq.get_clause(),
            {'range': {'a_field': {'lt': 10}}}
        )

    def test_when_min_val_and_max_val(self):

        rq = RangeQuery('a_field', min_val=1, max_val=10)
        self.assertEqual(
            rq.get_clause(),
            {'range': {'a_field': {'gte': 1, 'lt': 10}}}
        )