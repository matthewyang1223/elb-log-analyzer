#!/usr/bin/env python
"""Find all server error events within a time frame and report via slack."""

# standard library imports
import argparse
from calendar import timegm
from datetime import datetime, timedelta

# third party related imports
from elasticsearch import Elasticsearch

# local library imports
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
              'Default is 10 minutes ago.'),
        default=(now - minute * 10).isoformat()
    )
    ret.add_argument(
        '-e',
        '--end',
        help=('Specify when (%%Y-%%m-%%dT%%H:%%M:%%S) to stop scanning. '
              'Default is 5 minutes ago.'),
        default=(now - minute * 5).isoformat()
    )

    return ret


def query_server_error_records(begin_time, end_time):

    es = Elasticsearch(setting.get('elasticsearch', 'url'))
    indices = []
    day = timedelta(days=1)
    d = begin_time.date()

    while d <= end_time.date():
        indices.append('logstash-' + d.strftime('%Y.%m.%d'))
        d += day

    begin_at = timegm(begin_time.timetuple()) * 1000
    end_at = timegm(end_time.timetuple()) * 1000
    index = indices = ','.join(indices)
    offset = 0
    results = []
    body = {
        'filter': {
            'bool': {
                'must': [
                    {'range': {'timestamp': {'gte': begin_at, 'lt': end_at}}}
                ],
                'should': [
                    {'range': {'backend_status_code': {'gte': 500}}},
                    {'range': {'elb_status_code': {'gte': 500}}}
                ]
            }
        }
    }

    while True:
        body['from'] = offset
        result = es.search(
            index=index,
            body=body,
            sort='timestamp:asc',
            size=100,
        )
        logger.debug(result)
        hits = result.get('hits', {}).get('hits', [])

        if len(hits) == 0:
            break

        results.extend(map(lambda h: h['_source'], hits))
        offset += len(hits)

    return results


def main():

    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    begin_time = datetime.strptime(args.begin, '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(args.end, '%Y-%m-%dT%H:%M:%S')

    api_records = query_server_error_records(begin_time, end_time)

    if len(api_records) == 0:
        return

    map(lambda ar: ServerErrorMessage(ar).post(), api_records)


if __name__ == '__main__':

    main()
