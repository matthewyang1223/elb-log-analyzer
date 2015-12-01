#!/usr/bin/env python

# standard library imports
from contextlib import closing
from tempfile import NamedTemporaryFile

# third party related imports
import ujson

# local library imports
from elb_log_analyzer.actor.server_error_actor import ServerErrorActor
from elb_log_analyzer.aws.s3 import S3
from elb_log_analyzer.logger import logger
from elb_log_analyzer.logstash.logstash import Logstash


class ElbLogEventHandler(object):

    def __init__(self, message):

        self.s3_event = ujson.loads(message)
        self.actors = [
            ServerErrorActor()
        ]

    def handle(self):

        for record in self.s3_event['Records']:
            with closing(NamedTemporaryFile()) as raw_log:
                self.download_elb_log(record, raw_log.name)
                api_records = self.parse_elb_log(raw_log.name)

                for api_record in api_records:
                    for actor in self.actors:
                        actor.notify(api_record)

    def download_elb_log(self, event, output_fn):

        s3 = S3(event['s3']['bucket']['name'])
        s3.download(event['s3']['object']['key'], output_fn)

    def parse_elb_log(self, raw_log_fn):

        logger.info('Logstash starts...')
        ret = Logstash().parse(raw_log_fn)
        logger.info('Logstash finished')

        return ret
