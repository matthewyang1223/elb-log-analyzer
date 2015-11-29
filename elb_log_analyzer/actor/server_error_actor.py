#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from elb_log_analyzer.actor.base_actor import BaseActor
from elb_log_analyzer.config import setting


class ServerErrorActor(BaseActor):

    def __init__(self):

        super(ServerErrorActor, self).__init__()

    def should_respond(self, api_record):

        if api_record is None:
            return False

        elb_status_code = api_record.get('elb_status_code', 0)
        backend_status_code = api_record.get('backend_status_code', 0)

        return elb_status_code >= 500 or backend_status_code >= 500

    def respond(self, api_record):

        ctrl_action = api_record.get('rails', {}).get('controller#action', '')

        self.slack.chat.post_message(
            setting.get('slack', 'channel'),
            'Server error [%(ctrl_action)s]' % locals(),
            username='Optimus Prime Watchdog',
            attachments=self._make_attachments(api_record),
            icon_url=setting.get('slack', 'icon')
        )

    def _make_attachments(self, api_record):

        fallback = ' '.join([
            api_record['timestamp'],
            str(api_record['elb_status_code']),
            str(api_record['backend_status_code']),
            api_record.get('api', {}).get('http_verb', ''),
            api_record.get('api', {}).get('uri', '')
        ])

        return [
            {
                'fallback': fallback,
                'color': 'danger',
                'text': api_record['message']
            }
        ]
