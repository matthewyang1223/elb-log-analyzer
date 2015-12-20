#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
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

        es = self.get_es()
        trc = TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at)
        body = {
            'filter': trc.get_clause(),
            'aggs': {
                'avg_resp_time': {'avg': {'field': 'backend_processing_time'}}
            }
        }
        result = es.search(index=self.get_index_name(), body=body)
        logger.info(result)
        self._result = result['aggregations']['avg_resp_time']['value']

        return self._result


if __name__ == '__main__':

    from datetime import date, datetime
    artq = AvgResponseTimeQuery(date.today(), date.today() + date.resolution)
    print artq.query()
