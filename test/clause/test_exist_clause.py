#!/usr/bin/env python

# stadard library imports

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.clause.exist_clause import ExistClause


class TestGetClause(unittest.TestCase):

    def test(self):

        ec = ExistClause('data')
        self.assertEqual(ec.get_clause(), {'exists': {'field': 'data'}})
