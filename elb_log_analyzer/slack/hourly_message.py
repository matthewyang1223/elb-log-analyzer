#!/usr/bin/env python

# standard library imports
import math

# third party related imports

# local library imports
from elb_log_analyzer.slack.base_slack_message import BaseSlackMessage
from elb_log_analyzer.query.apdex_query import ApdexQuery
from elb_log_analyzer.query.avg_response_time_query import AvgResponseTimeQuery
from elb_log_analyzer.query.request_count_query import RequestCountQuery
from elb_log_analyzer.query.status_code_count_query import StatusCodeCountQuery


class HourlyMessage(BaseSlackMessage):

    APDEX_THRESHOLD = 0.05

    def __init__(self, begin_at, end_at):

        super(HourlyMessage, self).__init__()
        self.begin_at = begin_at
        self.end_at = end_at
        self._request_count = None

    def get_minutes(self):

        delta = self.end_at - self.begin_at
        return math.ceil(delta.total_seconds() / 60.0)

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
                    'value': '%.2f rpm' % (
                        1.0 * self.get_request_count() / self.get_minutes()
                    ),
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

        success = StatusCodeCountQuery.SUCCESS
        redirection = StatusCodeCountQuery.REDIRECTION
        client_error = StatusCodeCountQuery.CLIENT_ERROR
        server_error = StatusCodeCountQuery.SERVER_ERROR

        return {
            'color': '#fbb034',
            'title': 'HTTP summary',
            'fields': [
                {
                    'title': '2XX',
                    'value': self.get_http_status_code_count(success),
                    'short': True
                },
                {
                    'title': '3XX',
                    'value': self.get_http_status_code_count(redirection),
                    'short': True
                },
                {
                    'title': '4XX',
                    'value': self.get_http_status_code_count(client_error),
                    'short': True
                },
                {
                    'title': '5XX',
                    'value': self.get_http_status_code_count(server_error),
                    'short': True
                }
            ]
        }

    def get_request_count(self):

        if self._request_count is not None:
            return self._request_count

        rcq = RequestCountQuery(self.begin_at, self.end_at)
        self._request_count = rcq.query()

        return self._request_count

    def get_avg_response_time(self):

        return AvgResponseTimeQuery(self.begin_at, self.end_at).query()

    def get_apdex(self):

        aq = ApdexQuery(self.begin_at, self.end_at, self.APDEX_THRESHOLD)
        return aq.query()

    def get_http_status_code_count(self, status_code_class):

        sccq = StatusCodeCountQuery(
            self.begin_at,
            self.end_at,
            status_code_class
        )
        return sccq.query()
