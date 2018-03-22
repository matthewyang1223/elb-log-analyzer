#!/usr/bin/env python
"""Find all server error events within a time frame and report via slack."""

# standard library imports
import argparse
from calendar import timegm
from datetime import datetime, timedelta

# third party related imports
from elasticsearch import Elasticsearch

# local library imports
from elb_log_analyzer.clause.exist_clause import ExistClause
from elb_log_analyzer.clause.range_clause import RangeClause
from elb_log_analyzer.clause.term_clause import TermClause
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger
from elb_log_analyzer.slack.server_error_message import ServerErrorMessage


def init_arg_parser():

    ret = argparse.ArgumentParser(
        description='Find all server error events and report via slack.'
    )
    minute = timedelta(minutes=1)
    now = datetime.utcnow().replace(microsecond=0)

    ret.add_argument(
        '-b',
        '--begin',
        help=('Specify when (%%Y-%%m-%%dT%%H:%%M:%%S) to scan. '
              'Default is 15 minutes ago.'),
        default=(now - minute * 15).isoformat()
    )
    ret.add_argument(
        '-e',
        '--end',
        help=('Specify when (%%Y-%%m-%%dT%%H:%%M:%%S) to stop scanning. '
              'Default is 10 minutes ago.'),
        default=(now - minute * 10).isoformat()
    )

    return ret


def index_name(date):

    return 'logstash-' + date.strftime('%Y.%m.%d')


def query_server_error_records(begin_time, end_time):

    es_api = Elasticsearch(setting.get('elasticsearch', 'url'))
    indices = [
        index_name(begin_time.date() + timedelta(n))
        for n in xrange((end_time.date() - begin_time.date()).days)
    ]
    begin_at = timegm(begin_time.timetuple()) * 1000
    end_at = timegm(end_time.timetuple()) * 1000
    index = ','.join(indices) if indices else index_name(begin_time.date())
    offset = 0
    results = []
    body = {
        'query': {
            'bool': {
                'filter': [
                    RangeClause('timestamp', begin_at, end_at).get_clause(),
                    RangeClause('elb_status_code', 500).get_clause(),
                    # Filter out /robots.txt requests
                    ExistClause('rails.controller#action').get_clause(),
                    # Filter out https://52.197.62.134 requests
                    TermClause('domain_name', 'api.thekono.com').get_clause()
                ]
            }
        }
    }

    while True:
        body['from'] = offset
        args = dict(index=index, body=body, sort='timestamp:asc', size=100)
        result = es_api.search(**args)
        logger.debug(result)
        hits = result.get('hits', {}).get('hits', [])

        if not hits:
            break

        results.extend([h['_source'] for h in hits])
        offset += len(hits)

    return results


def main():

    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    begin_time = datetime.strptime(args.begin, '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(args.end, '%Y-%m-%dT%H:%M:%S')
    api_records = query_server_error_records(begin_time, end_time)

    if not api_records:
        return

    for api_record in api_records:
        ServerErrorMessage(api_record).post()


if __name__ == '__main__':

    main()
