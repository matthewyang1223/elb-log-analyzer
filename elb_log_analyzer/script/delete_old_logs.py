#!/usr/bin/env python
"""Dispose old access log

Delete archived access log stored in S3. Delete elasticsearch index
created by logstash.

"""

# standard library imports
import argparse
from datetime import date, datetime
import os.path

# third party related imports
from elasticsearch import Elasticsearch

# local library imports
from elb_log_analyzer.aws.s3 import S3
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger


def init_arg_parser():

    ret = argparse.ArgumentParser(description='Dispose old access log')
    ret.add_argument(
        '-d',
        '--date',
        help=('Specify what date (%%Y-%%m-%%d) to delete. '
              'Default is 30 days ago.'),
        default=(date.today() - date.resolution * 30).isoformat()
    )

    return ret


def delete_archived_log(target_date):

    s3 = S3(setting.get('elb_log_s3', 'bucket'))
    prefix = os.path.join(setting.get('elb_log_s3', 'archived_log_key_prefix'))
    key_name = os.path.join(prefix, '%s.zip' % target_date)
    s3.bucket.delete_key(key_name)
    logger.info('Delete object: %s', key_name)


def delete_elasticsearch_index(target_date):

    log_date = datetime.strptime(target_date, '%Y-%m-%d')
    index_name = 'logstash-%s' % log_date.strftime('%Y.%m.%d')
    es = Elasticsearch(setting.get('elasticsearch', 'url'))
    es.indices.delete(index=index_name)
    logger.info('Delete elasticsearch index: %s', index_name)


def main():

    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    delete_archived_log(args.date)
    delete_elasticsearch_index(args.date)


if __name__ == '__main__':

    main()
