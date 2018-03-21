#!/usr/bin/env python

# stadard library imports

# third party related imports

# local library imports


class ExistClause(object):

    def __init__(self, field):

        self.field = field

    def get_clause(self):

        return {'exists': {'field': self.field}}
