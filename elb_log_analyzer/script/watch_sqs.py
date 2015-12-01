#!/usr/bin/env python

# standard library imports

# third party related imports
import boto.sqs

# local library imports
from elb_log_analyzer.component.s3_event import S3Event
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger
from elb_log_analyzer.elb_log_event_handler import ElbLogEventHandler


def get_queue():

    conn = boto.sqs.connect_to_region(
        setting.get('elb_log_sqs', 'region'),
        aws_access_key_id=setting.get('aws', 'access_key'),
        aws_secret_access_key=setting.get('aws', 'secret_key')
    )
    return conn.get_queue(setting.get('elb_log_sqs', 'queue_name'))


def watch_sqs():

    queue = get_queue()
    if queue is None:
        msg = 'Cannot find queue'
        logger.error(msg)
        raise ValueError(msg)

    message = queue.read(wait_time_seconds=20)
    if message is None:
        logger.info('No message available now')
        return

    logger.info(message.get_body())
    s3_event = S3Event(message.get_body())

    try:
        ElbLogEventHandler(s3_event).handle()

    finally:
        queue.delete_message(message)
        logger.info('Delete SQS message')


def main():

    while True:
        try:
            watch_sqs()

        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':

    main()
