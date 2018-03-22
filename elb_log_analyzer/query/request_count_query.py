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


class RequestCountQuery(BaseTimeRangeQuery):

    def __init__(self, begin_at, end_at):

        super(RequestCountQuery, self).__init__(begin_at, end_at)
        self._result = None

    def query(self):

        if self._result is not None:
            return self._result

        conds = [
            TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at),
            ExistClause('rails.controller#action'),
            TermClause('domain_name', 'api.thekono.com'),
            RangeClause('backend_processing_time', 0)
        ]
        body = {'query': {'bool': {'filter': [c.get_clause() for c in conds]}}}
        result = self.get_es().count(index=self.get_index_name(), body=body)
        logger.info(result)
        self._result = result.get('count', 0)

        return self._result


if __name__ == '__main__':

    from datetime import date, datetime
    rcq = RequestCountQuery(date.today(), date.today() + date.resolution)
    print rcq.query()
