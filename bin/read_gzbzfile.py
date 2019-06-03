"""Read bz2 and gz file."""
import bz2
import gzip
import logging
import os


_logger = logging.getLogger(__name__)


class ReadGgBz2Normal(object):
    """Read file if it is gz or bz2 file."""

    def __init__(self, filename, filemode='rb'):
        """Init class."""
        self.filename = filename
        self.filemode = filemode
        if not os.path.isfile(self.filename):
            raise ValueError("Can not find file %s!" % self.filename)
        if self.filename.endswith('.gz'):
            self.handle = gzip.open(self.filename, self.filemode)
        elif self.filename.endswith('.bz2'):
            self.handle = bz2.open(self.filename, self.filemode)
        else:
            self.handle = open(self.filename, self.filemode)

    def __enter__(self):
        """Return self."""
        return self

    def __exit__(self, type, value, trace):
        """Exit file hanlde."""
        self.handle.close()

    def __iter__(self):
        """Return file itertion."""
        num = 0
        try:
            for num, line in enumerate(self.handle):
                yield line
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            if num <= 0 or not str(e).startswith('Not a gzipped file'):
                raise
            _logger.warn('decompression OK, trailing garbage ignored')

    def read(self, size=1024*1024*100):
        """Read file by size."""
        num = 0
        try:
            while True:
                chunk = self.handle(size)
                if chunk:
                    break
                else:
                    num += 1
                    yield chunk
        except (OSError, IOError) as e:  # IOError is needed for 2.7
            # ignore decompression OK, trailing garbage ignored
            if num <= 0 or not str(e).startswith('Not a gzipped file'):
                raise
            _logger.warn('decompression OK, trailing garbage ignored')
