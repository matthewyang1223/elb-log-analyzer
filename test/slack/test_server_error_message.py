#!/usr/bin/env python

# standard library imports

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.slack.server_error_message import ServerErrorMessage


API_RECORD = {
    "timestamp": "2015-12-09T09:40:01.558972Z",
    "rails": {
        "controller#action": "magazine_assets#cover",
        "format": None,
        "id": "565fac8a6b1ee",
        "size": "medium"
    },
    "api": {
        "query_string": None,
        "http_verb": "GET",
        "uri": "this is a uri",
        "path": "/KPI2/magazines/565fac8a6b1ee/cover/medium"
    },
    "backend_status_code": 500,
    "elb_status_code": 500,
    "message": "this is a message",
}


class TestGetText(unittest.TestCase):

    def setUp(self):

        self.message = ServerErrorMessage(API_RECORD)

    def test_call(self):

        self.assertEqual(
            self.message.get_text(),
            'Server error [magazine_assets#cover]'
        )


class TestGetAttachments(unittest.TestCase):

    def setUp(self):

        self.message = ServerErrorMessage(API_RECORD)

    def test_call(self):

        self.assertEqual(
            self.message.get_attachments(),
            [
                {
                    'fallback': (
                        '2015-12-09T09:40:01.558972Z 500 500 '
                        'GET /KPI2/magazines/565fac8a6b1ee/cover/medium'
                    ),
                    'color': 'danger',
                    'text': API_RECORD['message']
                }
            ]
        )