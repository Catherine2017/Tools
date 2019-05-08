"""

Get base count and error for fastq file both single end and pair end
sequencing.

"""

from itertools import zip_longest
import os
import re
import sys


class CheckFastq(object):
    """Get base count and error for fastq file."""

    base_count = 0
    read_count = 0
    pair = ['read1', 'read2']
    single_errors = [
        'The [{}] line:({}) have wrong base',
        'The [{}] line:({}) is not +',
        ('The 4th line length {} is not equal to the 2nd line length {}'
         ' at 4th line [{}]'),
        'The file don\'t have an integral multiple of 4 number of lines']
    pair_errors = [
        'Read1 name ({}) is not same with read2 name ({}) at line [{}]',
        'Read1 number is not equal to read2 number.']

    def set_value(self, filepath, pair_index):
        """Init value."""
        header = {'base_count': 0, 'read_count': 0, 'error': '',
                  'line2_len': 0, 'line4_len': 0, 'line_count': 0}
        readname = self.pair[pair_index]
        if filepath:
            if not os.path.isfile(filepath):
                raise ValueError("Can not find file %s!" % filepath)
            for key, value in header.items():
                setattr(self, '%s_%s' % (readname, key), value)
        else:
            if pair_index == 0:
                raise ValueError("The fastq file must be given!")
        return filepath

    def read_file(self, read1file, read2file="", read_gzbzfile="./"):
        """Read file."""
        self.base_count = 0
        self.read_count = 0
        self.read1file = self.set_value(read1file, 0)
        self.read2file = self.set_value(read2file, 1)
        iter2 = None
        if read_gzbzfile:
            if os.path.isdir(read_gzbzfile):
                dirpath = read_gzbzfile
            else:
                dirpath = os.path.dirname(read_gzbzfile)
            sys.path.append(dirpath)
            from read_gzbzfile import ReadGgBz2
            iter1 = ReadGgBz2(self.read1file)
            if self.read2file:
                iter2 = ReadGgBz2(self.read2file)
        else:
            iter1 = open(self.read1file)
            if self.read2file:
                iter2 = open(self.read2file)
        try:
            self.read_iter(iter1, iter2)
        finally:
            if not read_gzbzfile:
                iter1.close()
                if iter2 is not None:
                    iter2.close()

    def check_error(self):
        """Check whether has error."""
        errorlist = ['read1_error', 'read2_error', 'pair_error']
        tag = False
        for tmp in errorlist:
            if hasattr(self, tmp) and getattr(self, tmp):
                tag = True
                break
        return True

    def read_iter(self, iter1, iter2=None):
        """Run function."""
        iter_args = [iter1]
        if iter2 is not None:
            iter_args.append(iter2)
            self.pair_error = ''
        for i, lines in enumerate(zip_longest(*iter_args)):
            defi = (i + 1) % 4
            if lines:
                errors = []
                for j, line in enumerate(lines):
                    if line is None:
                        continue
                    self.__dict__['%s_line_count' % self.pair[j]] += 1
                    length = len(line)
                    error = ''
                    if defi == 1:
                        self.__dict__['%s_line2_len' % self.pair[j]] = 0
                        self.__dict__['%s_line4_len' % self.pair[j]] = 0
                    elif defi == 2:
                        self.__dict__['%s_line2_len' % self.pair[j]] = length
                        self.__dict__['%s_read_count' % self.pair[j]] += 1
                        self.__dict__['%s_base_count' % self.pair[j]] += length
                        line = line.upper()
                        if not set(line).issubset(set('ATCGN')):
                            error = self.single_errors[0].format(i, line)
                    elif defi == 3:
                        if line[0] != '+':
                            error = self.single_errors[1].format(i, line)
                    elif defi == 0:
                        self.__dict__['%s_line4_len' % self.pair[j]] = length
                        line2_len = getattr(
                            self, '%s_line2_len' % self.pair[j])
                        if line2_len != length:
                            error = self.single_errors[2].format(
                                length, line2_len, i)
                    if error:
                        self.__dict__['%s_error' % self.pair[j]] = error
                        errors.append(error)
                if len([x for x in lines if x is not None]) > 1:
                    if defi == 1:
                        origread = [x.split('\t')[0] for x in lines]
                        readnames = [re.sub(r'\w$', '', x) for x in origread]
                        if len(set(readnames)) != 1:
                            self.pair_error = self.pair_errors[0].format(
                                origread[0], origread[1], i)
                if any(errors) or (hasattr(self, 'pair_error') and
                       self.pair_error):
                    return False
        if iter2 is not None:
            if self.read1_read_count != self.read2_read_count:
                self.pair_error = self.pair_errors[1]
        for read in self.pair:
            key = '%s_line_count' % read
            if hasattr(self, key):
                value = getattr(self, key)
                if value % 4 != 0:
                    setattr(self, '%s_error' % key, self.single_errors[3])
        if self.check_error():
            return False
        else:
            total_stat = ['base_count', 'read_count']
            for astat in total_stat:
                for readname in self.pair:
                    if hasattr(self, '%s_%s' % (readname, astat)):
                        self.__dict__[astat] += getattr(self, '%s_%s' % (
                            readname, astat))
            return True


def test():
    """Test for module."""
    if len(sys.argv) < 2:
        print('Usage: python {0} read1.fq.gz [read2.fq.gz]'.format(
            sys.argv[0]))
        sys.exit(0)
    cf = CheckFastq()
    cf.read_file(*sys.argv[1:])
    print('=' * 24)
    print('-'*6, 'total statistics', '-'*6)
    print('total base count:', cf.base_count)
    print('total read count:', cf.read_count)
    single_info = ['base_count', 'read_count', 'error']
    for read in cf.pair:
        print('-'*6, read, 'information', '-'*6)
        for tmp in single_info:
            key = '%s_%s' % (read, tmp)
            if hasattr(cf, key):
                print('%s:%s' % (key, getattr(cf, key)))
    if hasattr(cf, 'pair_error'):
        print('-'*6, 'pair error', '-'*6)
        print('pair error:', cf.pair_error)


if __name__ == '__main__':
    test()
