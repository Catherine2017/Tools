"""Check compressed file whether is complete."""

import os
import subprocess


class CheckCompress(object):
    """Check compressed file wheher is complete."""

    def __init__(self, infile):
        """Init class."""
        self.infile = infile
        if not os.path.isfile(infile):
            raise ValueError("Can not find file %s!" % infile)

    def check(self):
        """Check compressed file."""
        pass

    def check_zip(self):
        """Unzip -t file."""
        import zipfile
        zip_file = zipfile.ZipFile(self.infile)
        ret = zip_file.testzip()
        if ret is not None:
            return False
        else:
            return True

    def check_gzip(self):
        """Gzip -t file."""
        try:
            subprocess.check_call('gzip -t %s' % self.infile, shell=True)
        except subprocess.CalledProcessError as callerror:
            if callerror.returncode > 1:
                return False
        return True
