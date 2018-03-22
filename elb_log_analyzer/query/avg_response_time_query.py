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


class AvgResponseTimeQuery(BaseTimeRangeQuery):

    def __init__(self, begin_at, end_at):

        super(AvgResponseTimeQuery, self).__init__(begin_at, end_at)
        self._result = None

    def query(self):

        if self._result is not None:
            return self._result

        field = 'backend_processing_time'
        conditions = [
            TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at),
            ExistClause('rails.controller#action'),
            TermClause('domain_name', 'api.thekono.com'),
            RangeClause(field, 0)
        ]
        body = {
            'query': {'bool': {'filter': [c.get_clause() for c in conditions]}},
            'size': 0,
            'aggs': {'avg_resp_time': {'avg': {'field': field}}}
        }
        result = self.get_es().search(index=self.get_index_name(), body=body)
        logger.info(result)
        self._result = result['aggregations']['avg_resp_time']['value']

        return self._result


if __name__ == '__main__':

    from datetime import date, datetime
    artq = AvgResponseTimeQuery(date.today(), date.today() + date.resolution)
    print artq.query()
