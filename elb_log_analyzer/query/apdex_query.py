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
from elb_log_analyzer.query.request_count_query import RequestCountQuery


class ApdexQuery(BaseTimeRangeQuery):

    def __init__(self, begin_at, end_at, apdex_threshold):

        super(ApdexQuery, self).__init__(begin_at, end_at)
        self.apdex_threshold = apdex_threshold
        self._result = None

    def query(self):

        if self._result is not None:
            return self._result

        satisfied = self.get_satisfied_request_count()
        tolerating = self.get_tolerating_request_count()
        request_count = self.get_request_count()
        self._result = (satisfied + 0.5 * tolerating) / request_count

        return self._result

    def get_satisfied_request_count(self):

        conditions = [
            TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at),
            ExistClause('rails.controller#action'),
            TermClause('domain_name', 'api.thekono.com'),
            RangeClause(
                'backend_processing_time',
                min_val=0,
                max_val=self.apdex_threshold
            )
        ]
        body = {'query': {'bool': {'filter': []}}}
        body['query']['bool']['filter'] = [c.get_clause() for c in conditions]

        result = self.get_es().count(index=self.get_index_name(), body=body)
        logger.info('satisifed: %s', result)

        return result.get('count', 0)

    def get_tolerating_request_count(self):

        conditions = [
            TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at),
            ExistClause('rails.controller#action'),
            TermClause('domain_name', 'api.thekono.com'),
            RangeClause(
                'backend_processing_time',
                min_val=self.apdex_threshold,
                max_val=self.apdex_threshold * 4
            )
        ]
        body = {'query': {'bool': {'filter': []}}}
        body['query']['bool']['filter'] = [c.get_clause() for c in conditions]

        result = self.get_es().count(index=self.get_index_name(), body=body)
        logger.info('tolerating: %s', result)

        return result.get('count', 0)

    def get_request_count(self):

        return RequestCountQuery(self.begin_at, self.end_at).query()


if __name__ == '__main__':

    from datetime import date
    aq = ApdexQuery(date.today(), date.today() + date.resolution, 0.05)
    print aq.query()
