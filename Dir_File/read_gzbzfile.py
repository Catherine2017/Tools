"""Read bz2 and gz file."""
import bz2
import gzip
import logging
import os


_logger = logging.getLogger(__name__)


class ReadGgBz2(object):
    """Read file if it is gz or bz2 file."""

    def __init__(self, filename):
        """Init class."""
        self.filename = filename
        if not os.path.isfile(self.filename):
            raise ValueError("Can not find file %s!" % self.filename)
        self.handle = None

    def __iter__(self):
        """Read file."""
        if self.filename.endswith('.gz'):
            self.handle = gzip.open(self.filename, 'rt')
        elif self.filename.endswith('.bz2'):
            self.handle = bz2.open(self.filename, 'rt')
        else:
            raise ValueError("File %s must be gz or bz2 compressed.\n" %
                             self.filename)
        num = 0
        try:
            for num, line in enumerate(self.handle):
                line = line.rstrip(os.linesep)
                yield line
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            if num <= 0 or not str(e).startswith('Not a gzipped file'):
                raise
            _logger.warn('decompression OK, trailing garbage ignored')
        finally:
            self.handle.close()
