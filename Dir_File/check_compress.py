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
        func = {'.gz': 'check_gzip', '.zip': 'check_zip'}
        file_ext = os.path.splitext(self.infile)[1]
        if file_ext in func:
            ret = getattr(self, func[file_ext])()
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
        else:
            return True

    def check_gzip(self):
        """Gzip -t file."""
        ret = True
        p = subprocess.Popen(
            ['gzip', '-t', self.infile], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stderr and b'decompression OK, trailing garbage ignored' \
                not in stderr:
            ret = False
        return ret
