#!/usr/bin/env python

# standard library imports

# third party related imports
from retrying import retry
from slacker import Slacker

# local library imports
from elb_log_analyzer.config import setting
from elb_log_analyzer.logger import logger


class BaseSlackMessage(object):

    def __init__(self):

        self.slack = Slacker(setting.get('slack', 'token'))

    def get_channel(self):

        return setting.get('slack', 'channel')

    def get_text(self):

        return 'this is text'

    def get_username(self):

        return 'Optimus Prime Watchdog'

    def get_as_user(self):

        return None

    def get_parse(self):

        return None

    def get_link_names(self):

        return None

    def get_attachments(self):

        return None

    def get_unfurl_links(self):

        return None

    def get_unfurl_media(self):

        return None

    def get_icon_url(self):

        return setting.get('slack', 'icon')

    def get_icon_emoji(self):

        return None

    @retry(stop_max_attempt_number=5)
    def post(self):

        try:
            self.slack.chat.post_message(
                self.get_channel(),
                self.get_text(),
                username=self.get_username(),
                as_user=self.get_as_user(),
                parse=self.get_parse(),
                link_names=self.get_link_names(),
                attachments=self.get_attachments(),
                unfurl_links=self.get_unfurl_links(),
                unfurl_media=self.get_unfurl_media(),
                icon_url=self.get_icon_url(),
                icon_emoji=self.get_icon_emoji()
            )

        except Exception as e:
            logger.exception(e)
            logger.error('Slack API failed, try again')

