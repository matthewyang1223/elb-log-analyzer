#!/usr/bin/env python

# standard library imports
import mimetypes

# third party related imports
import boto.s3
from boto.s3.key import Key

# local library imports
from elb_log_analyzer.component.measure_time import measure_time
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger


class ExceedMaxRetryError(Exception):
    """Raise when fail to upload constantly"""


class S3(object):

    def __init__(self, bucket_name):

        self.conn = boto.s3.connect_to_region(
            setting.get('elb_log_s3', 'region'),
            aws_access_key_id=setting.get('aws', 'access_key'),
            aws_secret_access_key=setting.get('aws', 'secret_key')
        )
        self.bucket = self.conn.get_bucket(bucket_name)

    @measure_time
    def download(self, key_name, filename):

        k = Key(self.bucket)
        k.key = key_name
        k.get_contents_to_filename(filename)

        logger.info('Download %s -> %s', key_name, filename)

    @measure_time
    def upload(self, key, filename, is_public=False, metadata=None):

        k = Key(self.bucket)
        k.key = key

        headers = {'Cache-Control': 'max-age=31536000'}
        content_type, encoding = mimetypes.guess_type(filename)
        if content_type is not None:
            headers['Content-Type'] = content_type
        if encoding == 'gzip':
            headers['Content-Encoding'] = 'gzip'

        if metadata is not None:
            for key in metadata:
                headers['x-amz-meta-' + key] = metadata[key]

        for _ in xrange(5):
            try:
                k.set_contents_from_filename(
                    filename,
                    headers=headers,
                    policy=('public-read' if is_public else 'private')
                )
                logger.info('Upload %s -> %s', filename, k.name)
                break

            except Exception as e:
                logger.exception(e)
                logger.warn('Try upload again')

        else:
            logger.error('Retry more than 5 times, give it up.')
            raise ExceedMaxRetryError()


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
