#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from elb_log_analyzer.clause.time_range_clause import TimeRangeClause
from elb_log_analyzer.logger import logger
from elb_log_analyzer.query.base_time_range_query import BaseTimeRangeQuery


class ApiExtendedStatQuery(BaseTimeRangeQuery):

    def __init__(self, begin_at, end_at):

        super(ApiExtendedStatQuery, self).__init__(begin_at, end_at)
        self._result = None

    def query(self):

        if self._result is not None:
            return self._result

        trc = TimeRangeClause(begin_time=self.begin_at, end_time=self.end_at)
        body = {
            'filter': trc.get_clause(),
            'size': 0,
            'aggs': {
                'apis': {
                    'terms': {
                        'field': 'rails.controller#action.raw',
                        'size': 0
                    },
                    'aggs': {
                        'stats': {
                            'extended_stats': {
                                'field': 'backend_processing_time'
                            }
                        }
                    }
                }
            }
        }
        result = self.get_es().search(index=self.get_index_name(), body=body)
        logger.info(result)

        obj = result.get('aggregations', {})
        obj = obj.get('apis', {})
        self._result = obj.get('buckets', [])

        return self._result


if __name__ == '__main__':

    from datetime import date
    aesq = ApiExtendedStatQuery(date.today(), date.today() + date.resolution)
    print aesq.query()
