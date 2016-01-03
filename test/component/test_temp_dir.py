#!/usr/bin/env python

# standard library imports
import os.path

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.component.temp_dir import TempDir


class TestTempDir(unittest.TestCase):

    def test_when_enter_context(self):

        with TempDir() as td:
            self.assertTrue(os.path.exists(td))
            self.assertTrue(os.path.isdir(td))

    def test_when_exit_context(self):

        with TempDir() as td:
            pass

        self.assertFalse(os.path.exists(td))
