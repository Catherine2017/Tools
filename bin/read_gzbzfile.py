"""Read bz2 and gz file."""
import bz2
import gzip
import logging
import os


_logger = logging.getLogger(__name__)


class ReadGgBz2Normal(object):
    """Read file if it is gz or bz2 file."""

    def __init__(self, filename, filemode='rb', dozcat=True):
        """Init class."""
        self.filename = filename
        self.filemode = filemode
        if not os.path.isfile(self.filename):
            raise ValueError("Can not find file %s!" % self.filename)
        if self.filename.endswith('.gz'):
            if dozcat and self._check_cmd('zcat'):
                self.zcat = self.zcat2line()
                self.handle = self.zcat.stdout
            else:
                self.handle = gzip.open(self.filename, self.filemode)
        elif self.filename.endswith('.bz2'):
            self.handle = bz2.open(self.filename, self.filemode)
        else:
            self.handle = open(self.filename, self.filemode)

    def _check_cmd(self, cmdname):
        """Check cmd whether in system environ."""
        check = False
        for cmdpath in os.environ['PATH'].split(':'):
            if os.path.isdir(cmdpath) and cmdname in os.listdir(cmdpath):
                check = True
                break
        return check

    def zcat2line(self):
        """Read gzip file by zcat."""
        import subprocess
        zcat = subprocess.Popen(['zcat', self.filename],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return zcat

    def __enter__(self):
        """Return self."""
        return self

    def __exit__(self, type, value, trace):
        """Exit file hanlde."""
        if not hasattr(self, 'zcat'):
            self.handle.close()

    def __iter__(self):
        """Return file itertion."""
        num = 0
        try:
            for num, line in enumerate(self.handle):
                if hasattr(self, 'zcat'):
                    line = line.decode('utf-8')
                yield line
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            self.check_error(num, e)
        if hasattr(self, 'zcat'):
            self.check_zcat_error()

    def check_error(self, num, e):
        """Check read error."""
        if self.filename.endswith('.gz') and num <= 0 or not str(e).startswith(
                'Not a gzipped file'):
            raise
        _logger.warn('decompression OK, trailing garbage ignored')

    def check_zcat_error(self):
        """Check zcat error."""
        self.zcat.wait()
        if self.zcat.returncode != 0:
            lines = self.zcat.stderr.readlines()
            if len(lines) > 1 and not lines[-1].endswith(
                    b'decompression OK, trailing garbage ignored\n'):
                raise ValueError("Failed to read file %s!" % self.filename)

    def read(self, size=1024*1024*100):
        """Read file by size."""
        num = 0
        try:
            while True:
                chunk = self.handle.read(size)
                if chunk:
                    break
                else:
                    num += 1
                    if hasattr(self, 'zcat'):
                        chunk = chunk.decode('utf-8')
                    yield chunk
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            self.check_error(num, e)
        if hasattr(self, 'zcat'):
            self.check_zcat_error()
