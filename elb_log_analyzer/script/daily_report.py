#!/usr/bin/env python
"""Daily report."""

# standard library imports
import argparse
from datetime import date, datetime

# third party related imports

# local library imports
from elb_log_analyzer.logger import logger
from elb_log_analyzer.slack.daily_message import DailyMessage


def init_arg_parser():

    ret = argparse.ArgumentParser(
        description='Daily report.'
    )
    yesterday = date.today() - date.resolution

    ret.add_argument(
        '-d',
        '--date',
        help=('Specify which date (%%Y-%%m-%%d) to make report. '
              'Default is yesterday.'),
        default=yesterday.isoformat()
    )

    return ret


def main():

    arg_parser = init_arg_parser()
    args = arg_parser.parse_args()

    target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    logger.info(target_date)

    DailyMessage(target_date).post()


if __name__ == '__main__':

    main()
