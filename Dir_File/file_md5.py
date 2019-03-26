"""Check md5 of file or generate md5."""
import hashlib
import os


class FileMD5(object):
    """Generate md5."""

    def __init__(self, filepath):
        """Init class."""
        filepath = os.path.abspath(filepath)
        if not os.path.isfile(filepath):
            raise ValueError("Can not find file %s!" % filepath)
        self.filepath = filepath

    @property
    def md5(self):
        """Get md5 of file."""
        hash_md5 = hashlib.md5()
        with open(self.filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def write_md5(self, outfile):
        """Write md5 of file to outfile."""
        with open(outfile, 'wt') as wt:
            wt.write('%s %s' % (self.filepath, self.md5))


def md5sum(md5file):
    """Md5sum -c file."""
    md5, filename = ('',) * 2
    with open(md5file) as wt:
        for line in wt:
            md5, filename = line.rstrip(os.linesep).strip().split()[:2]
            if md5:
                break
    if not md5:
        raise ValueError("Can not find md5 information!")
    filemd5 = FileMD5(filename).md5
    if filemd5 != md5:
        return False
    else:
        return True
