#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from elb_log_analyzer.clause.range_clause import RangeClause
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause
from elb_log_analyzer.logger import logger
from elb_log_analyzer.query.base_time_range_query import BaseTimeRangeQuery


class StatusCodeCountQuery(BaseTimeRangeQuery):

    SUCCESS = 200
    REDIRECTION = 300
    CLIENT_ERROR = 400
    SERVER_ERROR = 500
    STATUS_CODE_CLASSES = (SUCCESS, REDIRECTION, CLIENT_ERROR, SERVER_ERROR)

    def __init__(self, begin_at, end_at, status_code_class):

        super(StatusCodeCountQuery, self).__init__(begin_at, end_at)
        self.status_code_class = status_code_class
        self._result = None

        if status_code_class not in self.STATUS_CODE_CLASSES:
            raise ValueError(
                'Unknown status code class: %s' % status_code_class
            )

    def query(self):

        if self._result is not None:
            return self._result

        es = self.get_es()
        trc = TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at)
        rc = RangeClause(
            'backend_status_code',
            min_val=self.status_code_class,
            max_val=self.status_code_class + 100
        )
        body = {
            'filter': {
                'bool': {
                    'filter': [
                        trc.get_clause(),
                        rc.get_clause()
                    ]
                }
            }
        }
        result = es.count(index=self.get_index_name(), body=body)
        logger.info(result)
        self._result = result.get('count', 0)

        return self._result


if __name__ == '__main__':

    from datetime import date, datetime
    sccq = StatusCodeCountQuery(
        date.today(),
        date.today() + date.resolution,
        StatusCodeCountQuery.REDIRECTION
    )
    print sccq.query()
