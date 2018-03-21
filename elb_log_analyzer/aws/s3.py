#!/usr/bin/env python

# standard library imports
from contextlib import closing
import mimetypes

# third party related imports
import boto3
from retrying import retry

# local library imports
from elb_log_analyzer.component.measure_time import measure_time
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger


class ExceedMaxRetryError(Exception):
    """Raise when fail to upload constantly"""


class S3(object):

    def __init__(self, bucket_name):

        region = setting.get('elb_log_s3', 'region')
        self.client = boto3.client('s3', region_name=region)
        self.bucket = bucket_name

    @measure_time
    def download(self, key_name, filename):

        self.client.download_file(self.bucket, key_name, filename)
        logger.info('Download %s -> %s', key_name, filename)

    @measure_time
    @retry(stop_max_attempt_number=5)
    def upload(self, key, filename, is_public=False, metadata=None):

        content_type, encoding = mimetypes.guess_type(filename)

        with closing(open(filename)) as f:
            params = {
                'ACL': 'public-read' if is_public else 'private',
                'Body': f,
                'Bucket': self.bucket,
                'CacheControl': 'max-age=31536000',
                'Key': key
            }

            if content_type is not None:
                params['ContentType'] = content_type

            if encoding == 'gzip':
                params['ContentEncoding'] = 'gzip'

            if metadata is not None:
                params['Metadata'] = metadata.copy()

            self.client.put_object(**params)
            logger.info('Upload %s -> %s', filename, key)


if __name__ == '__main__':

    from contextlib import closing
    from tempfile import NamedTemporaryFile

    s3 = S3('kono-lb-logs')
    with closing(NamedTemporaryFile()) as f:
        s3.download(
            'optimus-prime/AWSLogs/127634673729/ELBAccessLogTestFile',
            f.name
        )
        print f.read()
