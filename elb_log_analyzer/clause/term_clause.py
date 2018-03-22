#!/usr/bin/env python

# stadard library imports

# third party related imports

# local library imports


class TermClause(object):

    def __init__(self, field, value):

        self.field = field
        self.value = value

    def get_clause(self):

        return {'term': {self.field: self.value}}
