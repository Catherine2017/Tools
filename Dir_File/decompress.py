"""Do decompressing comprressed file."""

import os
import sys


class Decompress(object):
    """Decompress compressd file."""

    def __init__(self, infile, outpath):
        """Init class."""
        self.infile = infile
        self.outpath = outpath
        if not os.path.isfile(infile):
            raise ValueError("Can not find this file %s!", infile)

    def un_gz(self, infile, outfile):
        """Decompress gzip file."""
        import subprocess
        try:
            subprocess.check_call('gunzip -c %s > %s', shell=True)
        except subprocess.CalledProcessError as e:
            raise

    @staticmethod
    def makedirs(dire):
        """Make diretory."""
        if not os.path.isdir(dire):
            os.makedirs(dire)

    def un_tar(self, file_name, outdir):
        """Untar zip file."""
        import tarfile
        tar = tarfile.open(file_name)
        names = tar.getnames()
        self.makedirs(outdir)
        for name in names:
            tar.extract(name, outdir)
        tar.close()

    def un_zip(self, file_name, outdir):
        """Unzip zip file."""
        import zipfile
        zip_file = zipfile.ZipFile(file_name)
        self.makedirs(outdir)
        for names in zip_file.namelist():
            zip_file.extract(names, outdir)
        zip_file.close()

    def un_rar(self, file_name, outdir):
        """Unrar zip file."""
        import rarfile
        nowdir = os.getcwd()
        try:
            rar = rarfile.RarFile(file_name)
            self.makedirs(outdir)
            os.chdir(outdir)
            rar.extractall(outdir)
            rar.close()
        finally:
            os.chdir(nowdir)

    def decompress(self):
        """Decompress."""
        func = {'.gz': 'un_gz', '.tar': 'un_tar', '.zip': 'un_zip',
                '.rar': 'un_rar'}
        file_ext = os.path.splitext(self.infile)[1]
        if self.infile.endswith('.tar.gz'):
            tempfile = os.path.join(self.outpath, 'tempfile.tmp.tar')
            self.un_gz(self.infile, tempfile)
            try:
                self.un_tar(tempfile, self.outpath)
            finally:
                os.remove(tempfile)
        elif file_ext in func:
            getattr(self, func[file_ext])(self.infile, self.outpath)
        else:
            raise ValueError("Can not find decompress method for %s!",
                             self.infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python {0} infile outpath\n'.format(sys.argv[0]))
        sys.exit(0)
    Decompress(*sys.argv[1:3]).decompress()
