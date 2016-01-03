#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# standard library imports
from collections import namedtuple
from datetime import timedelta

# third party related imports

# local library imports
from elb_log_analyzer.query.api_extended_stat_query import (
    ApiExtendedStatQuery
)
from elb_log_analyzer.slack.hourly_message import HourlyMessage


DAY = timedelta(days=1)


class DailyMessage(HourlyMessage):

    def __init__(self, target_date):

        super(DailyMessage, self).__init__(target_date, target_date + DAY)
        self.target_date = target_date
        self._api_extended_stats = None

    def get_text(self):

        return 'Daily report [%s]' % self.target_date.isoformat()

    def get_attachments(self):

        attachments = super(DailyMessage, self).get_attachments()
        attachments.append(self.make_popular_api_report())
        attachments.append(self.make_slowest_api_report())
        return attachments

    def make_popular_api_report(self):

        api_extended_stats = self.get_api_extended_stats()
        api_extended_stats.sort(key=lambda a: -1 * a.count)

        return {
            'color': '#ffdd00',
            'title': 'Top 10 popular API',
            'fields': [a.to_field() for a in api_extended_stats[:10]]
        }

    def make_slowest_api_report(self):

        api_extended_stats = self.get_api_extended_stats()
        api_extended_stats.sort(key=lambda a: -1 * a.avg)

        return {
            'color': '#c1d82f',
            'title': 'Top 10 slowest API',
            'fields': [a.to_field() for a in api_extended_stats[:10]]
        }

    def get_api_extended_stats(self):

        if self._api_extended_stats is not None:
            return self._api_extended_stats

        aesq = ApiExtendedStatQuery(self.target_date, self.target_date + DAY)
        result = aesq.query()
        api_stats = []

        for r in result:
            api_stats.append(
                ApiStat(
                    r['key'],
                    *(r['stats'][f] for f in ApiStat._fields[1:])
                )
            )

        self._api_extended_stats = api_stats
        return self._api_extended_stats


BaseApiStat = namedtuple(
    'BaseApiStat',
    ['controller_action', 'count', 'min', 'max', 'avg', 'std_deviation']
)

class ApiStat(BaseApiStat):

    __slots__ = ()

    def to_field(self):

        return {
            'title': self.controller_action,
            'short': False,
            'value': ', '.join([
                'count: %d' % self.count,
                'min: %.2f ms' % (self.min * 1000),
                'max: %.2f ms' % (self.max * 1000),
                'μ: %.2f ms' % (self.avg * 1000),
                'σ: %.2f ms' % (self.std_deviation * 1000)
            ])
        }
