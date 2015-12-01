#!/usr/bin/env python

# standard library imports

# third party related imports
import ujson

# local library imports


class S3Event(object):

    def __init__(self, event_string):

        self.parsed_obj = ujson.loads(event_string)

    @property
    def objects(self):

        if hasattr(self, '_objects'):
            return self._objects

        self._objects = []

        for record in self.parsed_obj.get('Records', []):
            s3 = record['s3']
            self._objects.append((s3['bucket']['name'], s3['object']['key']))

        return self._objects

