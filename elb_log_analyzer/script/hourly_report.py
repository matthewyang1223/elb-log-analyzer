#!/usr/bin/env python
"""Find all server error events within a time frame and report via slack."""

# standard library imports
import argparse
from datetime import datetime, timedelta

# third party related imports

# local library imports
from elb_log_analyzer.logger import logger
from elb_log_analyzer.slack.hourly_message import HourlyMessage


def init_arg_parser():

    ret = argparse.ArgumentParser(
        description='Find all server error events and report via slack.'
    )
    hour = timedelta(hours=1)
    top_of_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    ret.add_argument(
        '-b',
        '--begin',
        help=('Specify when (%%Y-%%m-%%dT%%H:%%M:%%S) to scan. '
              'Default is 1 hour before the top of this hour.'),
        default=(top_of_hour - hour).isoformat()
    )
    ret.add_argument(
        '-e',
        '--end',
        help=('Specify when (%%Y-%%m-%%dT%%H:%%M:%%S) to stop scanning. '
              'Default is the top of this hour.'),
        default=(top_of_hour).isoformat()
    )

    return ret


def main():

    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    begin_time = datetime.strptime(args.begin, '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(args.end, '%Y-%m-%dT%H:%M:%S')
    logger.info(begin_time)
    logger.info(end_time)

    HourlyMessage(begin_time, end_time).post()


if __name__ == '__main__':

    main()
