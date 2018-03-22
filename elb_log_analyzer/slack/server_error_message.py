#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from elb_log_analyzer.slack.base_slack_message import BaseSlackMessage


class ServerErrorMessage(BaseSlackMessage):

    def __init__(self, api_record):

        super(ServerErrorMessage, self).__init__()
        self.api_record = api_record

    def get_text(self):

        controller_action = self.api_record['rails']['controller#action']
        return 'Server error [%(controller_action)s]' % locals()

    def get_attachments(self):

        fallback = ' '.join([
            self.api_record['timestamp'],
            str(self.api_record['elb_status_code']),
            str(self.api_record.get('backend_status_code', '-')),
            self.api_record.get('api', {}).get('http_verb', ''),
            self.api_record.get('api', {}).get('path', '')
        ])

        return [
            {
                'fallback': fallback,
                'color': 'danger',
                'text': self.api_record['message']
            }
        ]
