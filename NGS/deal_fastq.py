"""Get base count and error for fastq file both single end and pair end sequencing."""
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
        'Read1 name {} is not same with read2 name %s at line [{}]',
        'Read1 number is not equal to read2 number.']

    def set_value(self, filepath, pair_index):
        """Init value."""
        header = {'base_count': 0, 'read_count': 0, 'error': '',
                  'line2_len': 0, 'line4_len': 0}
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

    def read_file(self, read1file, read2file="", read_gzbzfile=""):
        """Read file."""
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

    def read_iter(self, iter1, iter2=None):
        """Run function."""
        iter_args = [iter1]
        if iter2 is not None:
            iter_args.extend(iter2)
            self.pair_error = ''
        for i, lines in enumerate(zip_longest(*iter_args)):
            defi = (i + 1) % 4
            if lines:
                errors = []
                for j, line in enumerate(lines):
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
                if any(errors):
                    return False
                if len(lines) > 1:
                    if any(x is None for x in lines):
                        self.pair_error = self.pair_errors[1]
                    if defi == 1:
                        readnames = [re.sub(r'\w$', '', x.split()[0])
                                     for x in lines]
                        if len(set(readnames)) != 1:
                            self.pair_error = self.pair_errors[0].format(
                                readnames[0], readnames[1], i)
                    if self.pair_error:
                        return False
        if (i+1) % 4 != 0:
            self.read1_error = self.single_errors[3]
            if iter2 is not None and not self.pair_error:
                self.read2_error = self.single_errors[3]
            return False
        else:
            total_stat = ['base_count', 'read_count']
            for astat in total_stat:
                for readname in self.pair:
                    if hasattr(self, '%s_%s' % (readname, astat)):
                        self.__dict__[astat] += getattr(self, '%s_%s' % (
                            readname, astat))
            return True
