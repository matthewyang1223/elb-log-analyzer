#!/usr/bin/env python

# standard library imports
from contextlib import closing
import os.path
import subprocess
from tempfile import gettempdir
import uuid
from zipfile import ZipFile

# third party related imports

# local library imports


class ZipCompressor(object):

    @classmethod
    def compress(cls, target_dir, output_file, password=None):

        tmp_zip = os.path.join(gettempdir(), uuid.uuid1().hex + '.zip')
        cmd = ['zip', '--recurse-paths']
        password is not None and cmd.extend(['--password', password])
        cmd.extend([tmp_zip, '.'])

        try:
            with closing(open(os.devnull, 'w')) as null:
                p = subprocess.Popen(cmd, cwd=target_dir,
                                     stdout=null, stderr=null)
                p.wait()

            with closing(open(tmp_zip, 'rb')) as i:
                with closing(open(output_file, 'wb')) as o:
                    o.write(i.read())

        finally:
            os.path.exists(tmp_zip) and os.unlink(tmp_zip)

    @classmethod
    def uncompress(cls, target_file, output_dir, password=None):

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with closing(ZipFile(target_file)) as z:
            password is not None and z.setpassword(password)
            z.extractall(output_dir)
