#!/usr/bin/env python

# standard library imports

# third party related imports
from slacker import Slacker

# local library imports
from config import setting


class BaseActor(object):

    def __init__(self):

        self.init_slack()

    def notify(self, api_record):

        if not self.should_respond(api_record):
            return

        self.respond(api_record)

    def should_respond(self, api_record):

        raise NotImplementedError()

    def init_slack(self):

        self.slack = Slacker(setting.get('slack', 'token'))
