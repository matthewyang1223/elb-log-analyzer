#!/usr/bin/env python

# stadard library imports

# third party related imports

# local library imports


class RangeClause(object):

    def __init__(self, field, min_val=None, max_val=None):

        if min_val is None and max_val is None:
            raise ValueError('Not a valid query')

        self.field = field
        self.min_val = min_val
        self.max_val = max_val

    def get_clause(self):

        ret = {'range': {self.field: {}}}
        obj = ret['range'][self.field]

        if self.min_val is not None:
            obj['gte'] = self.min_val

        if self.max_val is not None:
            obj['lt'] = self.max_val

        return ret
