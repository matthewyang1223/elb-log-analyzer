#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from elb_log_analyzer.clause.exist_clause import ExistClause
from elb_log_analyzer.clause.range_clause import RangeClause
from elb_log_analyzer.clause.term_clause import TermClause
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause
from elb_log_analyzer.logger import logger
from elb_log_analyzer.query.base_time_range_query import BaseTimeRangeQuery


class ApiExtendedStatQuery(BaseTimeRangeQuery):
    """Get extended stats group by API"""

    GROUP_BY_FIELD = 'rails.controller#action'

    def __init__(self, begin_at, end_at, order_by='count', asc=True, limit=10):

        super(ApiExtendedStatQuery, self).__init__(begin_at, end_at)
        self.order_by = order_by
        self.asc = asc
        self.limit = limit
        self._result = None

    def query(self):

        if self._result is not None:
            return self._result

        agg = self.bucket_strategy()
        agg.update(self.sub_aggregation())
        agg = {'apis': agg}
        body = {'query': self.query_clauses(), 'size': 0, 'aggs': agg}
        result = self.get_es().search(index=self.get_index_name(), body=body)
        logger.info(result)

        obj = result.get('aggregations', {})
        obj = obj.get('apis', {})
        self._result = obj.get('buckets', [])

        return self._result

    def query_clauses(self):

        conditions = [
            TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at),
            ExistClause(self.GROUP_BY_FIELD),
            TermClause('domain_name', 'api.thekono.com'),
            RangeClause('backend_processing_time', 0)
        ]

        return {'bool': {'filter': [c.get_clause() for c in conditions]}}

    def bucket_strategy(self):

        return {
            'terms': {
                'field': self.GROUP_BY_FIELD + '.keyword',
                'size': self.limit,
                'order': {
                    ('stats.' + self.order_by): 'asc' if self.asc else 'desc'
                }
            }
        }

    def sub_aggregation(self):

        return {
            'aggs': {
                'stats': {
                    'extended_stats': {'field': 'backend_processing_time'}
                }
            }
        }


if __name__ == '__main__':

    from datetime import date
    aesq = ApiExtendedStatQuery(date.today(), date.today() + date.resolution)
    print aesq.query()
