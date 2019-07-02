"""Read bz2 and gz file."""
import bz2
from functools import wraps
import gzip
import logging
import os
import sys

_logger = logging.getLogger(__name__)


class ReadGgBz2Normal(object):
    """Read file if it is gz or bz2 file."""

    def __init__(self, filename, dozcat=True):
        """Init class."""
        self.filename = filename
        self.error = 'Failed to read %s' % os.path.basename(filename)
        if not os.path.isfile(self.filename):
            raise IOError("Can not find file %s" % self.filename)
        if self.filename.endswith('.gz'):
            if dozcat and self._check_cmd('zcat'):
                self.zcat = self.zcat2line()
                self.handle = self.zcat.stdout
            else:
                self.handle = gzip.open(self.filename, 'rt')
        elif self.filename.endswith('.bz2'):
            self.handle = bz2.open(self.filename, 'rt')
        else:
            self.handle = open(self.filename, 'rt')

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

    def __exit__(self, atype, value, trace):
        """Exit file hanlde."""
        if not hasattr(self, 'zcat'):
            self.handle.close()

    def __iter__(self):
        """Return file itertion."""
        line = None
        try:
            for line in self.handle:
                if hasattr(self, 'zcat'):
                    line = line.decode('utf-8')
                yield line
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            self.check_error(line, e)
        except Exception as e:
            _logger.exception(e)
            raise ValueError(self.error)
        if hasattr(self, 'zcat'):
            self.check_zcat_error()

    def check_error(self, line, e):
        """Check read error."""
        if self.filename.endswith('.gz') and line is not None and line and \
                str(e).startswith('Not a gzipped file'):
            sys.stdout.write('decompression OK, trailing garbage ignored\n')
        else:
            _logger.exception(e)
            raise ValueError(self.error)

    def check_zcat_error(self):
        """Check zcat error."""
        self.zcat.wait()
        if self.zcat.returncode != 0:
            lines = self.zcat.stderr.readlines()
            if len(lines) > 1 and not lines[-1].endswith(
                    b'decompression OK, trailing garbage ignored\n'):
                raise ValueError(self.error)

    def read_fastq(self):
        """Read file by size."""
        tag, lines = None, []
        try:
            for line in self.handle:
                if hasattr(self, 'zcat'):
                    line = line.decode('utf-8')
                lines.append(line.rstrip(os.linesep).strip())
                if len(lines) >= 4:
                    tag = 1
                    yield lines
                    lines = []
            if lines:
                yield lines
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            self.check_error(tag, e)
        except Exception as e:
            _logger.exception(e)
            raise ValueError(self.error)
        if hasattr(self, 'zcat'):
            self.check_zcat_error()


def runtime(func):
    """Get running time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        sys.stdout.write('%s running time:%s\n' % (
            func.__name__, end-start))
        return res
    return wrapper


@runtime
def by_gzip(fastq):
    import gzip
    with gzip.open(fastq, 'rt') as rd:
        for line in rd:
            pass


@runtime
def by_rg(fastq, dozcat=False):
    with ReadGgBz2Normal(fastq, dozcat) as rd:
        for line in rd:
            pass


@runtime
def by_fastq(fastq1, dozcat=False):
    with ReadGgBz2Normal(fastq1, dozcat) as r1:
        for lines in r1.read_fastq():
            pass
        sys.stdout.write('lines last:%s\n' % len(lines))

@runtime
def by_pairfastq(fastq1, fastq2, dozcat=False):
    from itertools import izip_longest
    try:
        with ReadGgBz2Normal(fastq1, dozcat) as r1,\
                ReadGgBz2Normal(fastq2, dozcat) as r2:
            for lines in izip_longest(r1.read_fastq(),
                                      r2.read_fastq()):
                pass
    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stdout.write('Usage:python {0} fastq1 [fastq2]\n'.format(
            sys.argv[0]))
        sys.exit(1)
    # by_gzip(sys.argv[1])
    # by_rg(sys.argv[1])
    # by_fastq(sys.argv[1])
    # by_rg(sys.argv[1], True)
    if len(sys.argv) == 3:
        by_pairfastq(sys.argv[1], sys.argv[2], False)
    else:
        by_fastq(sys.argv[1],  False)
