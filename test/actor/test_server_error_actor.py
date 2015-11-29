#!/usr/bin/env python

# standard library imports
import random

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.actor.server_error_actor import ServerErrorActor


class TestShouldRespond(unittest.TestCase):

    def setUp(self):

        self.actor = ServerErrorActor()
        self.api = {
            'elb_status_code': 200,
            'backend_status_code': 200
        }

    def test_when_elb_status_code_is_5XX(self):

        self.api['elb_status_code'] = random.choice(xrange(500, 599))
        self.assertTrue(self.actor.should_respond(self.api))

    def test_when_backend_status_code_is_5XX(self):

        self.api['backend_status_code'] = random.choice(xrange(500, 599))
        self.assertTrue(self.actor.should_respond(self.api))

    def test_when_status_code_is_not_5XX(self):

        self.api['elb_status_code'] = random.choice(xrange(200, 500))
        self.api['backend_status_code'] = random.choice(xrange(200, 500))
        self.assertFalse(self.actor.should_respond(self.api))
