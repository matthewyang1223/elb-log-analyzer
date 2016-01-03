#!/usr/bin/env python

# standard library imports
from contextlib import closing
from tempfile import NamedTemporaryFile

# third party related imports

# local library imports
from elb_log_analyzer.actor.server_error_actor import ServerErrorActor
from elb_log_analyzer.aws.s3 import S3
from elb_log_analyzer.logger import logger
from elb_log_analyzer.logstash.logstash import Logstash


class ElbLogEventHandler(object):

    def __init__(self, event):

        self.event = event
        self.actors = [
            ServerErrorActor()
        ]

    def handle(self):

        for bucket_name, key_name in self.event.objects:
            with closing(NamedTemporaryFile()) as raw_log:
                self.download_elb_log(bucket_name, key_name, raw_log.name)
                api_records = self.parse_elb_log(raw_log.name)

                for api_record in api_records:
                    for actor in self.actors:
                        actor.notify(api_record)

    def download_elb_log(self, bucket_name, key_name, output_fn):

        s3 = S3(bucket_name)
        s3.download(key_name, output_fn)

    def parse_elb_log(self, raw_log_fn):

        logger.info('Logstash starts...')
        ret = Logstash().parse(raw_log_fn)
        logger.info('Logstash finished')

        return ret
