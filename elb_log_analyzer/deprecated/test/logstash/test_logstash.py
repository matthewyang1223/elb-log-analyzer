#!/usr/bin/env python

# standard library imports
from contextlib import closing
from tempfile import NamedTemporaryFile
import os.path

# third party related imports
from mock import patch
from mock import MagicMock
import ujson
import unittest2 as unittest

# local library imports
from elb_log_analyzer.logstash.logstash import Logstash


module = 'elb_log_analyzer.logstash.logstash'


class TestGenerateConfig(unittest.TestCase):

    def setUp(self):

        self.logstash = Logstash()

    def test_call(self):

        conf = self.logstash.generate_config('/tmp/logstash.conf')

        with closing(open(self.logstash.tmpl_path)) as i:
            data = i.read().decode('utf8')
            data = data.replace('{{output_name}}', '/tmp/logstash.conf')
            data = data.replace(
                '{{route_spec_name}}',
                self.logstash.route_spec_path
            )

        self.assertEqual(conf.strip(), data.strip())


class TestCallLogstash(unittest.TestCase):

    def setUp(self):

        self.logstash = Logstash()

    @patch(module + '.open')
    @patch(module + '.subprocess')
    def test_call(self, mock_subprocess_module, mock_open_func):

        conf_fn = '/tmp/logstash.conf'
        raw_log_fn = '/tmp/access.log'

        mock_open_func.return_value = mock_file = MagicMock()
        mock_subprocess_module.check_call.return_value = 0

        self.logstash.call_logstash(conf_fn, raw_log_fn)
        mock_open_func.assert_called_with(raw_log_fn, 'rb')
        call_args, call_kwargs = mock_subprocess_module.check_call.call_args

        self.assertEqual(
            call_args[0],
            [self.logstash.logstash_script, '-f', conf_fn]
        )
        self.assertEqual(call_kwargs['stdin'], mock_file)


class TestParseLogstashOutput(unittest.TestCase):

    def setUp(self):

        self.logstash = Logstash()

    def test_call(self):

        logstash_outputs = [{"hello": "world"}, {"wow": "wow"}]
        serailized_logstash_outputs = map(ujson.dumps, logstash_outputs)

        self.assertEqual(
            self.logstash.parse_logstash_output(serailized_logstash_outputs),
            logstash_outputs
        )


class TestParse(unittest.TestCase):

    def setUp(self):

        self.logstash = Logstash()
        self.mock_route_spec()
        self.generate_log()

    def tearDown(self):

        if os.path.exists(self.sample_route_spec):
            os.unlink(self.sample_route_spec)

        if os.path.exists(self.access_log):
            os.unlink(self.access_log)

    def mock_route_spec(self):

        with closing(NamedTemporaryFile(delete=False)) as f:
            f.write('GET /users/:id(.:format) users#show')
            self.sample_route_spec = f.name
            self.logstash.route_spec_path = f.name

    def generate_log(self):

        with closing(NamedTemporaryFile(delete=False)) as f:
            self.user_agent = unicode(
                'Mozilla/5.0 (iPhone; CPU iPhone OS 9_0_2 like Mac OS X) '
                'AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13A452 '
                '[FBAN/FBIOS;FBAV/42.0.0.40.154;FBBV/16331253;FBDV/iPhone6,2;'
                'FBMD/iPhone;FBSN/iPhone OS;FBSV/9.0.2;FBSS/2; FBCR/'
            )
            self.message = unicode(
                '2015-11-08T13:18:22.739395Z lb-api 116.241.3.237:62314 '
                '10.151.132.178:80 0.00006 0.013716 0.000044 200 200 0 166 '
                '"GET https://api.thekono.com:443/KPI2/users/1 HTTP/1.1" '
                '"Mozilla/5.0 (iPhone; CPU iPhone OS 9_0_2 like Mac OS X) '
                'AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13A452 '
                '[FBAN/FBIOS;FBAV/42.0.0.40.154;FBBV/16331253;FBDV/iPhone6,2;'
                'FBMD/iPhone;FBSN/iPhone OS;FBSV/9.0.2;FBSS/2; FBCR/" '
                'ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2\n'
            )
            f.write(self.message)
            self.access_log = f.name

    def test_call(self):

        result = self.logstash.parse(self.access_log)
        self.assertEqual(
            result,
            [
                {
                    u"backend_processing_time": 0.013715999999999999,
                    u"client_ip": u"116.241.3.237",
                    u"received_bytes": 0,
                    u"sent_bytes": 166,
                    u"timestamp": u"2015-11-08T13:18:22.739395Z",
                    u"@timestamp": u"2015-11-08T13:18:22.739Z",
                    u"rails": {
                        u"controller#action": u"users#show",
                        u"id": u"1",
                        u"format": None
                    },
                    u"client_port": 62314,
                    u"request_processing_time": 0.00006000000000000001,
                    u"host": u"yuliang-ThinkPad-X230",
                    u"api": {
                        u"query_string": None,
                        u"http_verb": u"GET",
                        u"uri": u"https://api.thekono.com:443/KPI2/users/1",
                        u"path": u"/KPI2/users/1"
                    },
                    u"backend_status_code": 200,
                    u"backend_ip": u"10.151.132.178",
                    u"elb_status_code": 200,
                    u"useragent": {
                        u"major": u"42",
                        u"os_name": u"iOS",
                        u"name": u"Facebook",
                        u"os_minor": u"0",
                        u"os_major": u"9",
                        u"agent": self.user_agent,
                        u"patch": u"0",
                        u"device": u"iPhone6,2",
                        u"os": u"iOS 9.0.2",
                        u"minor": u"0"
                    },
                    u"message": self.message.strip(),
                    u"response_processing_time": 0.000044000000000000006,
                    u"@version": u"1",
                    u"geoip": {
                        u"region_name": u"03",
                        u"latitude": 25.039199999999994,
                        u"ip": u"116.241.3.237",
                        u"continent_code": u"AS",
                        u"country_code3": u"TWN",
                        u"country_code2": u"TW",
                        u"city_name": u"Taipei",
                        u"longitude": 121.52499999999998,
                        u"country_name": u"Taiwan",
                        u"timezone": u"Asia/Taipei",
                        u"real_region_name": u"T'ai-pei",
                        u"location": [
                            121.52499999999998,
                            25.039199999999994
                        ]
                    },
                    u"loadbalancer": u"lb-api",
                    u"backend_port": 80
                }
            ]
        )
