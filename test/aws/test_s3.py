#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import patch
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.aws.s3 import S3


module = 'elb_log_analyzer.aws.s3'


class TestDownload(unittest.TestCase):

    @patch(module + '.boto.s3')
    def setUp(self, mock_boto_s3_module):

        self.bucket_name = 'qq'
        mock_boto_s3_module.connect_to_region.return_value = MagicMock()
        self.s3 = S3(self.bucket_name)

    @patch(module + '.Key')
    def test_call(self, mock_key_cls):

        mock_key_cls.return_value = mock_key = MagicMock()
        self.s3.download('key_name', 'filename')

        mock_key_cls.assert_called_with(self.s3.bucket)
        print str(mock_key.key)
        self.assertEqual(mock_key.key, 'key_name')
        mock_key.get_contents_to_filename.assert_called_with('filename')
