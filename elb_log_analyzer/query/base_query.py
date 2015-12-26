#!/usr/bin/env python

# standard library imports

# third party related imports
from elasticsearch import Elasticsearch

# local library imports
from elb_log_analyzer.config import setting


class BaseQuery(object):

    def get_es(self):

        return Elasticsearch(setting.get('elasticsearch', 'url'))
