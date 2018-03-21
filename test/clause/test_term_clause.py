#!/usr/bin/env python

# stadard library imports

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.clause.term_clause import TermClause


class TestGetClause(unittest.TestCase):

    def test(self):

        tc = TermClause('field', 'value')
        self.assertEqual(tc.get_clause(), {'term': {'field': 'value'}})
