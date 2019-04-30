"""Read bz2 and gz file."""
import bz2
import gzip
import subprocess


class ReadGgBz2(object):
    """Read file if it is gz or bz2 file."""

    def __init__(self, filename, gzippath='gzip', gunzippath='gunzip'):
        """Init class."""
        self.filename = filename
        self.gzippath = gzippath
        self.gunzippath = gunzippath
        self.handle = None
        if filename.endswith('.gz'):
            self.handle = gzip.open(filename, 'rt')
        elif filename.endswith('.bz2'):
            self.handle = bz2.open(filename, 'rt')
        else:
            raise ValueError("File must be gz or bz2 compressed.\n")

    def __iter__(self):
        """Read file."""
        fail_read = True
        try:
            for line in self.handle:
                yield line
        except Exception:
            fail_read = False
        finally:
            self.handle.close()
        if fail_read and self.filename.endswith('.gz'):
            stderr = self.run_cmd([self.gzip, '-t', self.filename])
            if b'decompression OK, trailing garbage ignored' in stderr:
                pass

    @staticmethod
    def run_cmd(args):
        """Run system."""
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stderr
