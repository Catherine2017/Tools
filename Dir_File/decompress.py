"""Do decompressing comprressed file."""

import gzip
import os
import rarfile
import sys
import tarfile
import zipfile


class Decompress(object):
    """Decompress compressd file."""

    def __init__(self, infile, outpath):
        """Init class."""
        self.infile = infile
        self.outpath = outpath
        if os.path.isfile(infile):
            raise ValueError("Can not find this file %s!", infile)

    def un_gz(self, infile, outfile):
        """Decompress gzip file."""
        g_file = gzip.GzipFile(infile)
        with open(outfile, 'w+') as wt:
            wt.write(g_file.read())

    @staticmethod
    def makedirs(dire):
        """Make diretory."""
        if not os.path.isdir(dire):
            os.makedirs(dire)

    def un_tar(self, file_name, outdir):
        """Untar zip file."""
        tar = tarfile.open(file_name)
        names = tar.getnames()
        self.makedirs(outdir)
        for name in names:
            tar.extract(name, outdir)
        tar.close()

    def un_zip(self, file_name, outdir):
        """Unzip zip file."""
        zip_file = zipfile.ZipFile(file_name)
        self.makedirs(outdir)
        for names in zip_file.namelist():
            zip_file.extract(names, outdir)
        zip_file.close()

    def un_rar(self, file_name, outdir):
        """Unrar zip file."""
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
        if self.infile.endswith('.tar.gz'):
            tempfile = os.path.join(self.outpath, 'tempfile.tmp.tar')
            self.un_gz(self.infile, tempfile)
            try:
                self.un_tar(tempfile, self.outpath)
            finally:
                os.remove(tempfile)
        elif self.infile.endswith('.gz'):
            self.un_gz(self.infile, self.outpath)
        elif self.infile.endswith('.tar'):
            self.un_tar(self.infile, self.outpath)
        elif self.infile.endswith('.zip'):
            self.un_zip(self.infile, self.outpath)
        elif self.infile.endswith('.rar'):
            self.un_rar(self.infile, self.outpath)
        else:
            raise ValueError("Can not find decompress method for %s!",
                             self.infile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python {0} infile outpath\n'.format(sys.argv[0]))
        sys.exit(0)
    Decompress(*sys.argv[1:3]).decompress()
