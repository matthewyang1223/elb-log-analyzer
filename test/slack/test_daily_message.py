#!/usr/bin/env python

# standard library imports
from datetime import date

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.slack.daily_message import DailyMessage


class TestGetText(unittest.TestCase):

    def setUp(self):

        self.d = date(2016, 1, 1)
        self.dm = DailyMessage(self.d)

    def test(self):

        self.assertEqual(self.dm.get_text(), 'Daily report [2016-01-01]')
