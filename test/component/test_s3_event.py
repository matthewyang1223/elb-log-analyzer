#!/usr/bin/env python

# standard library imports

# third party related imports
import ujson
import unittest2 as unittest

# local library imports
from elb_log_analyzer.component.s3_event import S3Event


class TestObjects(unittest.TestCase):

    def setUp(self):

        self.event = S3Event(ujson.dumps({
            "Records": [
                {
                    "eventVersion": "2.0",
                    "eventSource": "aws:s3",
                    "awsRegion": "ap-southeast-1",
                    "eventTime": "2015-11-24T14:38:18.077Z",
                    "eventName": "ObjectCreated:CompleteMultipartUpload",
                    "userIdentity": {
                        "principalId": "AWS:XXX"
                    },
                    "requestParameters": {
                        "sourceIPAddress": "54.54.54.54"
                    },
                    "responseElements": {
                        "x-amz-request-id": "2460BBE2D69475B6",
                        "x-amz-id-2": "QYxqrD"
                    },
                    "s3": {
                        "s3SchemaVersion": "1.0",
                        "configurationId": "NewElbLogCreated",
                        "bucket": {
                            "name": "elb-logs",
                            "ownerIdentity": {
                                "principalId": "A12"
                            },
                            "arn": "arn:aws:s3:::elb-logs"
                        },
                        "object": {
                            "key": "an-object",
                            "size": 753057,
                            "eTag": "969df253159ab2a270867710d5ca3c58-1",
                            "sequencer": "0056547659D01839EA"
                        }
                    }
                }
            ]
        }))

    def test_call(self):

        self.assertEqual(self.event.objects, [('elb-logs', 'an-object')])
