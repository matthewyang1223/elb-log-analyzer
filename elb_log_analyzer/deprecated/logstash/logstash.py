#!/usr/bin/env python

# standard library imports
from contextlib import closing
import logging
import os.path
import subprocess
from tempfile import NamedTemporaryFile

# third party related imports
from jinja2 import Template
import ujson

# local library imports
from elb_log_analyzer.config import setting


class Logstash(object):

    def __init__(self):

        self.logstash_script = setting.get('logstash', 'script')
        self.route_spec_path = setting.get('logstash', 'route_spec')
        cwd = os.path.abspath(os.path.dirname(__file__))
        self.tmpl_path = os.path.join(cwd, 'logstash.conf.jinja2')

    def parse(self, raw_log_fn):

        with closing(NamedTemporaryFile()) as logstash_output_f:
            with closing(NamedTemporaryFile()) as conf_f:
                conf = self.generate_config(logstash_output_f.name)
                conf_f.write(conf.encode('utf8'))
                conf_f.flush()

                self.call_logstash(conf_f.name, raw_log_fn)
                return self.parse_logstash_output(logstash_output_f)

    def generate_config(self, logstash_output_fn):

        ctx = {
            'output_name': logstash_output_fn,
            'route_spec_name': self.route_spec_path
        }

        with closing(open(self.tmpl_path)) as f:
            tmpl = Template(f.read().decode('utf8'))
            return tmpl.render(**ctx)

    def call_logstash(self, config_fn, raw_log_fn):

        cmd = [self.logstash_script, '-f', config_fn]

        with closing(open(os.devnull, 'w')) as o:
            with closing(open(raw_log_fn, 'rb')) as r:
                ret_code = subprocess.check_call(cmd, stdin=r, stdout=o)

                if ret_code != 0:
                    message_tmpl = 'logstash fails to parse "%(raw_log_fn)"'
                    message = message_tmpl % locals()
                    raise RuntimeError(message)

    def parse_logstash_output(self, logstash_output_file):

        api_records = []

        for line in logstash_output_file:
            try:
                api_records.append(ujson.loads(line))
            except Exception as e:
                logging.exception(e)
                logging.error(line)

        return api_records
