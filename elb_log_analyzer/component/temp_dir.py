#!/usr/bin/env python
"""Provide a temporary folder utility involving the with statement"""

# standard library imports
import os.path
import shutil
from tempfile import mkdtemp

# third party related imports

# local library imports


class TempDir(object):

    def __enter__(self):

        self.tempdir = mkdtemp()
        return self.tempdir

    def __exit__(self, exc_type, exc_value, traceback):

        os.path.exists(self.tempdir) and shutil.rmtree(self.tempdir)
