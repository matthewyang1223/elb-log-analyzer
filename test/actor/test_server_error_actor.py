#!/usr/bin/env python

# standard library imports
import random

# third party related imports
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.actor.server_error_actor import ServerErrorActor
from elb_log_analyzer.config import setting


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


class TestRespond(unittest.TestCase):

    def setUp(self):

        self.actor = ServerErrorActor()
        self.actor.slack = MagicMock()
        self.api = {
            'api': {
                'http_verb': 'POST',
                'uri': '/users'
            },
            'rails': {
                'controller#action': 'users#create'
            },
            'timestamp': '2015-01-01 00:00:00',
            'elb_status_code': 500,
            'backend_status_code': 500,
            'message': 'this is message'
        }

    def test_call(self):

        self.actor.respond(self.api)
        self.actor.slack.chat.post_message.assert_called_with(
            setting.get('slack', 'channel'),
            'Server error [users#create]',
            username='Optimus Prime Watchdog',
            attachments=[
                {
                    'fallback': '2015-01-01 00:00:00 500 500 POST /users',
                    'color': 'danger',
                    'text': 'this is message'
                }
            ],
            icon_url=setting.get('slack', 'icon')
        )
