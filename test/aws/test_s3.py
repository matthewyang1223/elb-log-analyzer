#!/usr/bin/env python

# standard library imports
import os.path

# third party related imports
from mock import patch
from mock import MagicMock
import unittest2 as unittest

# local library imports
from elb_log_analyzer.aws.s3 import S3


module = 'elb_log_analyzer.aws.s3'


class TestDownload(unittest.TestCase):

    @patch(module + '.boto3')
    def setUp(self, mock_boto_s3_module):

        self.bucket_name = 'qq'
        self.s3 = S3(self.bucket_name)
        self.s3.client = MagicMock()

    def test_call(self):

        self.s3.download('key_name', 'filename')
        self.s3.client.download_file.assert_called_with(
            self.bucket_name,
            'key_name',
            'filename'
        )


class TestUpload(unittest.TestCase):

    def setUp(self):

        self.bucket_name = 'qq'

        self.s3 = S3(self.bucket_name)
        self.s3.client = MagicMock()

        self.filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'lena.jpg'
        )

    @patch(module + '.open')
    def test_when_private(self, mock_open):

        mock_open.return_value = mock_file = MagicMock()

        self.s3.upload('key_name', self.filename, False, {'happy': ':)'})
        self.s3.client.put_object.assert_called_with(
            ACL='private',
            Body=mock_file,
            Bucket=self.bucket_name,
            CacheControl='max-age=31536000',
            ContentType='image/jpeg',
            Metadata={'happy': ':)'},
            Key='key_name'
        )

    @patch(module + '.open')
    def test_when_public(self, mock_open):

        mock_open.return_value = mock_file = MagicMock()

        self.s3.upload('key_name', self.filename, True, {'happy': ':)'})
        self.s3.client.put_object.assert_called_with(
            ACL='public-read',
            Body=mock_file,
            Bucket=self.bucket_name,
            CacheControl='max-age=31536000',
            ContentType='image/jpeg',
            Metadata={'happy': ':)'},
            Key='key_name'
        )
