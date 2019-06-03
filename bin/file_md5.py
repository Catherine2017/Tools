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
            wt.write('%s  %s' % (self.md5, self.filepath))

    def md5check(self, md5):
        """Check md5 file."""
        if self.md5 != md5:
            return False
        else:
            return True


def md5sum(md5file):
    """Md5sum -c file."""
    md5, filename = ('',) * 2
    with open(md5file) as wt:
        for line in wt:
            if line.startswith("MD5"):
                filename, md5 = line.split('=')
                filename = filename.replace('MD5(', '').replace(')', '')
            else:
                md5, filename = line.split('  ')[:2]
            md5 = md5.strip()
            filename = filename.strip()
            filemd5 = FileMD5(filename)
            infor = 'succeed' if filemd5.md5check(md5) else 'fail'
            print('{} md5 check: {}'.format(filename, infor))
