#!/usr/bin/env python

# standard library imports
from contextlib import closing
import os.path
import subprocess
from tempfile import NamedTemporaryFile
import uuid
from zipfile import ZipFile

# third party related imports
import unittest2 as unittest

# local library imports
from elb_log_analyzer.component.temp_dir import TempDir
from elb_log_analyzer.component.zip_compressor import ZipCompressor


class BaseTestCase(object):

    def create_folder_content(self, folder):

        with closing(open(os.path.join(folder, 'foo'), 'w')) as f:
            f.write('bar')

        subdir = os.path.join(folder, 'hello')
        os.mkdir(subdir)

        with closing(open(os.path.join(subdir, 'world'), 'w')) as f:
            f.write('hello world!')


    def check_folder_content(self, folder):

        with closing(open(os.path.join(folder, 'foo'))) as f:
            self.assertEqual(f.read(), 'bar')

        subdir = os.path.join(folder, 'hello')

        with closing(open(os.path.join(subdir, 'world'))) as f:
            self.assertEqual(f.read(), 'hello world!')


class TestCompress(unittest.TestCase, BaseTestCase):

    def test_when_no_password(self):

        zipped_file = os.path.join('/tmp', uuid.uuid1().hex + '.zip')

        with TempDir() as folder:
            self.create_folder_content(folder)
            ZipCompressor.compress(folder, zipped_file)

        with TempDir() as folder:
            with closing(open(os.devnull, 'w')) as null:
                subprocess.check_call(
                    ['unzip', zipped_file, '-d', folder],
                    stdout=null,
                    stderr=null
                )
                self.check_folder_content(folder)

        os.unlink(zipped_file)

    def test_when_there_is_password(self):

        with closing(NamedTemporaryFile(suffix='.zip')) as zipped_file:
            with TempDir() as folder:
                self.create_folder_content(folder)
                ZipCompressor.compress(folder, zipped_file.name, password='ok')

            with TempDir() as folder:
                with closing(ZipFile(zipped_file.name)) as zf:
                    zf.extractall(path=folder, pwd='ok')
                    self.check_folder_content(folder)


class TestUncompress(unittest.TestCase, BaseTestCase):

    def test_when_no_password(self):

        with TempDir() as folder:
            self.create_folder_content(folder)

            with closing(NamedTemporaryFile(suffix='.zip')) as zf:
                ZipCompressor.compress(folder, zf.name)

                with TempDir() as folder:
                    ZipCompressor.uncompress(zf.name, folder)
                    self.check_folder_content(folder)

    def test_uncompress_with_password(self):

        with closing(NamedTemporaryFile(suffix='.zip')) as zipped_file:
            with TempDir() as folder:
                self.create_folder_content(folder)
                ZipCompressor.compress(folder, zipped_file.name, 'apple')

            with TempDir() as folder:
                ZipCompressor.uncompress(
                    zipped_file.name,
                    folder,
                    password='apple'
                )
                self.check_folder_content(folder)
