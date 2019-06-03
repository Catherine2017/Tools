"""Check compressed file whether is complete."""

import os
import subprocess


class CheckCompress(object):
    """Check compressed file wheher is complete."""

    def __init__(self, infile, gzippath='gzip', bz2path='bzip2'):
        """Init class."""
        self.infile = infile
        if not os.path.isfile(infile):
            raise ValueError("Can not find file %s!" % infile)
        self.gzippath = gzippath
        self.bz2path = bz2path
        self.error = ""

    def check(self):
        """Check compressed file."""
        func = ('.gz', '.zip', '.bz2')
        file_ext = os.path.splitext(self.infile)[1]
        if file_ext in func:
            ret = getattr(self, 'check_%s' % (file_ext.lstrip('.')))()
        else:
            raise ValueError("Can not find check compressed method for %s!",
                             self.infile)
        return ret

    def check_zip(self):
        """Unzip -t file."""
        import zipfile
        zip_file = zipfile.ZipFile(self.infile)
        ret = zip_file.testzip()
        if ret is not None:
            return False
            self.error = 'Failed to test for zip file %s!' % self.infile
        else:
            return True

    @staticmethod
    def run_cmd(args):
        """Run system."""
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stderr.decode('utf-8').strip(os.linesep).strip()

    def check_gz(self):
        """Gzip -t file."""
        ret = True
        stderr = self.run_cmd([self.gzippath, '-t', self.infile])
        if stderr and 'decompression OK, trailing garbage ignored' \
                not in stderr:
            ret = False
            self.error = stderr
        return ret

    def check_bz2(self):
        """Bzip -tv file."""
        ret = True
        stderr = self.run_cmd([self.bz2path, '-tv', self.infile])
        if stderr and not stderr.endswith('ok\n'):
            ret = False
            self.error = stderr
        return ret
