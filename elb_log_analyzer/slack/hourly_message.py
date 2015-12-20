#!/usr/bin/env python

# standard library imports
from datetime import timedelta

# third party related imports
from elasticsearch import Elasticsearch

# local library imports
from elb_log_analyzer.clause.range_clause import RangeClause
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger
from elb_log_analyzer.slack.base_slack_message import BaseSlackMessage
from elb_log_analyzer.query.avg_response_time_query import AvgResponseTimeQuery
from elb_log_analyzer.query.request_count_query import RequestCountQuery


class HourlyMessage(BaseSlackMessage):

    APDEX_THRESHOLD = 0.05

    def __init__(self, begin_at, end_at):

        super(HourlyMessage, self).__init__()
        self.es = Elasticsearch(setting.get('elasticsearch', 'url'))
        self.begin_at = begin_at
        self.end_at = end_at
        self.index_name = self.get_index_name()

    def get_index_name(self):

        d = self.begin_at.date()
        e = self.end_at.date()
        day = timedelta(days=1)
        span = []

        while d <= e:
            span.append(d)
            d += day

        return ','.join(['logstash-' + s.strftime('%Y.%m.%d') for s in span])

    def get_text(self):

        b = self.begin_at.isoformat()
        e = self.end_at.isoformat()
        return 'Brief report [%(b)s ~ %(e)s]' % locals()

    def get_attachments(self):

        return [
            self.make_apdex_report(),
            self.make_status_code_report()
        ]

    def make_apdex_report(self):

        return {
            'color': '#ff0000',
            'title': 'Server summary',
            'fields': [
                {
                    'title': 'Req count',
                    'value': self.get_request_count(),
                    'short': True
                },
                {
                    'title': 'Avg resp time',
                    'value': '%.2f ms' % (self.get_avg_response_time() * 1000),
                    'short': True
                },
                {
                    'title': 'Throughput',
                    'value': '%.2f rpm' % (self.get_request_count() / 60.0),
                    'short': True
                },
                {
                    'title': 'Apdex (%s)' % self.APDEX_THRESHOLD,
                    'value': '%.2f' % self.get_apdex(),
                    'short': True
                }
            ]
        }

    def make_status_code_report(self):

        return {
            'color': '#fbb034',
            'title': 'HTTP sumary',
            'fields': [
                {
                    'title': '2XX',
                    'value': self.get_http_status_code_count(200),
                    'short': True
                },
                {
                    'title': '3XX',
                    'value': self.get_http_status_code_count(300),
                    'short': True
                },
                {
                    'title': '4XX',
                    'value': self.get_http_status_code_count(400),
                    'short': True
                },
                {
                    'title': '5XX',
                    'value': self.get_http_status_code_count(500),
                    'short': True
                }
            ]
        }

    def get_request_count(self):

        return RequestCountQuery(self.begin_at, self.end_at).query()

    def get_avg_response_time(self):

        return AvgResponseTimeQuery(self.begin_at, self.end_at).query()

    def get_apdex(self):

        body = {
            'filter': {
                'bool': {
                    'filter': [
                        self._build_timestamp_filter(),
                        self._build_value_filter(
                            'backend_processing_time',
                            max_val=self.APDEX_THRESHOLD
                        )
                    ]
                }
            }
        }
        result = self.es.count(index=self.index_name, body=body)
        logger.info(result)
        satisfied = result.get('count', 0)

        body = {
            'filter': {
                'bool': {
                    'filter': [
                        self._build_timestamp_filter(),
                        self._build_value_filter(
                            'backend_processing_time',
                            min_val=self.APDEX_THRESHOLD,
                            max_val=self.APDEX_THRESHOLD * 4
                        )
                    ]
                }
            }
        }
        result = self.es.count(index=self.index_name, body=body)
        logger.info(result)
        tolerating = result.get('count', 0)

        return (satisfied + 0.5 * tolerating) / self.get_request_count()

    def get_http_status_code_count(self, num):

        body = {
            'filter': {
                'bool': {
                    'filter': [
                        self._build_timestamp_filter(),
                        self._build_value_filter(
                            'backend_status_code',
                            num,
                            num + 100
                        )
                    ]
                }
            }
        }
        result = self.es.count(index=self.index_name, body=body)
        logger.info(result)

        return result.get('count', 0)

    def _build_timestamp_filter(self):

        trq = TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at)
        return trq.get_clause()

    def _build_value_filter(self, field, min_val=None, max_val=None):

        return RangeClause(field, min_val, max_val).get_clause()
