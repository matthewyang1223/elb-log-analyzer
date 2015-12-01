#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import patch
from mock import MagicMock
import ujson
import unittest2 as unittest

# local library imports
from elb_log_analyzer.elb_log_event_handler import ElbLogEventHandler


module = 'elb_log_analyzer.elb_log_event_handler'


class TestDownloadElbLog(unittest.TestCase):

    def setUp(self):

        self.event = {
            's3': {
                'bucket': {'name': 'a-bucket'},
                'object': {'key': 'an-object'}
            }
        }
        self.handler = ElbLogEventHandler('{}')

    @patch(module + '.S3')
    def test_call(self, mock_s3_cls):

        mock_s3_cls.return_value = mock_s3_obj = MagicMock()
        self.handler.download_elb_log(self.event, '/somewhere')

        mock_s3_cls.assert_called_with('a-bucket')
        mock_s3_obj.download.assert_called_with('an-object', '/somewhere')


class TestParseElbLog(unittest.TestCase):

    def setUp(self):

        self.handler = ElbLogEventHandler('{}')

    @patch(module + '.Logstash')
    def test_call(self, mock_logstash_cls):

        mock_logstash_cls.return_value = mock_logstash_obj = MagicMock()
        self.handler.parse_elb_log('/somewhere')
        mock_logstash_obj.parse.assert_called_with('/somewhere')


class TestHandle(unittest.TestCase):

    def setUp(self):

        self.handler = ElbLogEventHandler('{"Records": [{}]}')
        mock_actor = MagicMock()
        self.handler.actors = [mock_actor]

    def test_call(self):

        self.handler.download_elb_log = mock_download_elb_log = MagicMock()
        self.handler.parse_elb_log = mock_parse_elb_log = MagicMock()
        mock_api_record = MagicMock()

        mock_parse_elb_log.return_value = [mock_api_record]

        self.handler.handle()
        self.assertEqual(mock_download_elb_log.call_args[0][0], {})
        self.assertEqual(
            mock_download_elb_log.call_args[0][1],
            mock_parse_elb_log.call_args[0][0]
        )
        self.handler.actors[0].notify.assert_called_with(mock_api_record)
