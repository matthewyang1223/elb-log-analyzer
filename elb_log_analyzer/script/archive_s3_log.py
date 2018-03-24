#!/usr/bin/env python
"""Archive elb access log

Download all elb access logs of a given date. Compress them into a zip
file and then upload to S3. In the end, those elb access logs are
deleted.

"""

# standard library imports
import argparse
from contextlib import closing
from datetime import date, datetime
import os.path
from tempfile import NamedTemporaryFile

# third party related imports
from concurrent import futures

# local library imports
from elb_log_analyzer.aws.s3 import S3
from elb_log_analyzer.component.measure_time import measure_time
from elb_log_analyzer.component.temp_dir import TempDir
from elb_log_analyzer.component.zip_compressor import ZipCompressor
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger


def init_arg_parser():

    ret = argparse.ArgumentParser(
        description='Archive elb logs stored in s3 of a date.'
    )
    ret.add_argument(
        '-d',
        '--date',
        help=('Specify what date (%%Y-%%m-%%d) to archive. '
              'Default is yesterday.'),
        default=(date.today() - date.resolution).isoformat()
    )

    return ret


def download_log(s3, key_name, output_folder):

    basename = os.path.basename(key_name)
    s3.download(key_name, os.path.join(output_folder, basename))
    return key_name


@measure_time
def download_logs_of_a_date(log_date, output_folder):

    log_date = datetime.strptime(log_date, '%Y-%m-%d')
    key_prefix = setting.get('elb_log_s3', 'log_key_prefix')
    key_prefix = ''.join([key_prefix, log_date.strftime('%Y/%m/%d')])
    s3 = S3(setting.get('elb_log_s3', 'bucket'))
    key_names = []

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        for key_name in s3.list(key_prefix):
            executor.submit(download_log, s3, key_name, output_folder)
            key_names.append(key_name)

    logger.info('Download all logs on %s', log_date.isoformat())
    return key_names


def upload_to_s3(filename, log_date):

    s3 = S3(setting.get('elb_log_s3', 'bucket'))
    prefix = os.path.join(setting.get('elb_log_s3', 'archived_log_key_prefix'))
    key_name = os.path.join(prefix, '%s.zip' % log_date)
    s3.upload(key_name, filename)
    logger.info('Upload %s', key_name)


def delete_logs(key_names):

    s3 = S3(setting.get('elb_log_s3', 'bucket'))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        for key_name in key_names:
            executor.submit(s3.delete, key_name)

    logger.info('Delete archived logs')


def main():

    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    with TempDir() as tempdir:
        key_names = download_logs_of_a_date(args.date, tempdir)

        if not key_names:
            logger.warn('Cannot find any log on %s', args.date)
            return

        with closing(NamedTemporaryFile(suffix='.zip')) as zip_file:
            ZipCompressor.compress(tempdir, zip_file.name)
            upload_to_s3(zip_file.name, args.date)

        delete_logs(key_names)


if __name__ == '__main__':

    main()
