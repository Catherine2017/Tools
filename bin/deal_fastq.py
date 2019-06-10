# -*- coding:utf-8 -*-

"""
Description: Get base count and error for fastq file both single end and pair
             end sequencing.
"""

from copy import deepcopy
import itertools
import logging
import os
import re
import sys
import time

from read_gzbzfile import ReadGgBz2Normal

if sys.version.startswith('3'):
    zip_longest = itertools.zip_longest
else:
    zip_longest = itertools.izip_longest
_logger = logging.getLogger(__name__)
errors = {
    'WB': 'The [{0}] line:({1}) have wrong base',
    'NF': 'The [{0}] line:({1}) is not {2}',
    'DL': ('The 4th line length {0} is not equal to the 2nd line length {1}'
           ' at 4th line [{2}]'),
    'OQ': ('The ord of qualiyty ({0[0]}-{0[1]}) is out of {1[0]}-{1[1]} at'
           ' line [{2}]'),
    'RN': 'Read1 name ({0}) is not same with read2 name ({1}) at line [{2}]',
    'FF': "Failed to read file: {0}",
    'N4': r'The file don\'t have an integral multiple of 4 number of lines',
    'NE': 'Read1 number is not equal to read2 number at line [{0}].'}


class lazypropery(object):
    """Return value if exists."""

    def __init__(self, func):
        """Init class."""
        self.func = func

    def __get__(self, instance, cls):
        """Get function."""
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class SingleRead(object):
    """Get information for single read."""

    phredrange = (33, 126)
    phredQ = (58, 75)

    def __init__(self, number, lines4):
        """Init class."""
        # number: start from 0
        self.readnumber = number
        self.lines4 = lines4

    @lazypropery
    def check_len(self):
        """Get lines length."""
        if self.lines4 is None or len(self.lines4) != 4:
            return True
        else:
            return False

    @lazypropery
    def line2_len(self):
        """Get line2 length."""
        if self.check_len:
            return 0
        return len(self.lines4[1])

    @lazypropery
    def phreds(self):
        """Get phred for read."""
        if self.check_len:
            return (59, 59)
        aset = set(map(ord, self.lines4[3]))
        phred_min = min(aset)
        phred_max = max(aset)
        return (phred_min, phred_max)

    @lazypropery
    def error(self):
        """Check error."""
        def check_first(linenum, line, first):
            if line[0] == first:
                return ""
            else:
                return errors['NF'].format(linenum, line, first)
        # 检查是否为4的倍数
        if self.check_len:
            return errors['N4']
        # 检查第二行是否为ATCG0123
        if not set(self.lines4[1].upper()).issubset(set('ATGCN0123')):
            return errors['WB'].format(self.readnumber*4+1, self.lines4[1])
        # 检查第一行和第三行是否为@或+开头
        firsts = {0: '@', 2: '+'}
        for i, first in firsts.items():
            error = check_first(self.readnumber*4+i, self.lines4[i], first)
            if error:
                return error
        # 检查第二行和第四行是否相等
        line4_number = self.readnumber*4+3
        line4_len = len(self.lines4[3])
        if self.line2_len != line4_len:
            return errors['DL'].format(self.line2_len, line4_len, line4_number)
        if self.phreds[0] < self.phredrange[0] or \
                self.phreds[1] > self.phredrange[1]:
            return errors['OQ'].format(self.phreds, self.phredrange,
                                       line4_number)
        return ""

    @lazypropery
    def readname(self):
        """Get read name."""
        if self.check_len:
            return ""
        readname = self.lines4[0].strip().partition('\t')[0]\
            .partition(" ")[0]
        return readname

    @lazypropery
    def phreq_set(self):
        """Get phreq for read."""
        phreq_set = ''
        if self.phreds[0] <= self.phredQ[0]:
            phreq_set = '33'
        elif self.phreds[1] >= self.phredQ[1]:
            phreq_set = '64'
        return phreq_set

    @lazypropery
    def base_count(self):
        """Get base count for read."""
        return self.line2_len


class PairRead(object):
    """Get information for pair read."""
    readname_normal = re.compile(r'(\/[12])|(\.[fr])$')
    casava_1_8 = re.compile(
        r'^@([a-zA-Z0-9_-]+:\d+:[a-zA-Z0-9_-]+:\d+:\d+:[0-9-]+:'
        r'[0-9-]+)(\s+|\:)([12]):[YN]:\d*[02468]:?([ACGTN\_\+\d+]*)$')


    def __init__(self, number, lines1, lines2):
        """Init class."""
        self.number = number
        self.linenum = self.number*4
        self.lines1 = lines1
        self.lines2 = lines2
        self.read1 = SingleRead(number, lines1)
        self.read2 = SingleRead(number, lines2)

    def get_com_name(self, string):
        if self.readname_normal.search(string):
            return self.readname_normal.sub('', string)
        pattern = self.casava_1_8.search(string)
        if pattern:
            return pattern.group(1)
        return string

    @lazypropery
    def pair_error(self):
        """Check pair error."""
        # 检查read1和read2数目是否一致
        if self.lines1 is None or self.lines2 is None:
            return errors['NE'].format(self.linenum)
        # 检查read1和read2的名称是否一致
        if self.get_com_name(self.read1.readname) != self.get_com_name(
                self.read2.readname):
            return errors['RN'].format(
                self.read1.readname, self.read2.readname, self.linenum)
        return ""


class HoldSingle(object):
    """Hold single fastq."""

    def __init__(self):
        """Init class."""
        self.error = ''
        self.phreq_set = ''
        self.base_count = 0
        self.read_count = 0

    def add(self, singleread):
        """Add single read."""
        self.read_count += 1
        self.base_count += singleread.base_count
        if not self.phreq_set:
            self.phreq_set = singleread.phreq_set

    def check_error(self, singleread):
        """Check error."""
        self.error = singleread.error
        if self.error:
            return True
        else:
            return False


class HoldPair(object):
    """Hold pair read."""

    def __init__(self):
        """Init class."""
        self.pair_error = ''
        self.read1 = HoldSingle()
        self.read2 = HoldSingle()
        self.base_count = 0
        self.read_count = 0
        self.phreq_set = ""

    def add(self, pairread):
        """Add pair read."""
        self.read1.add(pairread.read1)
        self.read2.add(pairread.read2)

    def cal(self):
        """Calculate pair read."""
        self.read_count = self.read1.read_count + self.read2.read_count
        self.base_count = self.read1.base_count + self.read2.base_count
        self.phreq_set = self.read1.phreq_set if self.read1.phreq_set else \
            self.read2.phreq_set

    def check_error(self, pairread):
        """Check error."""
        self.pair_error = pairread.pair_error
        if self.pair_error:
            return True
        if self.read1.check_error(pairread.read1):
            return True
        if self.read2.check_error(pairread.read2):
            return True
        return False


class ReadFastq(object):
    """Read fastq and get read unit."""

    def __init__(self, fastqfile):
        """Init class."""
        self.fastqfile = fastqfile
        if not os.path.isfile(fastqfile):
            raise ValueError("Can not find file %s!" % fastqfile)

    def __iter__(self):
        """Get lines."""
        lines = []
        try:
            with ReadGgBz2Normal(self.fastqfile, 'rt') as rg:
                for line in rg:
                    line = line.rstrip(os.linesep)
                    lines.append(line)
                    if len(lines) >= 4:
                        yield lines
                        lines = []
                if lines:
                    yield lines
        except Exception as e:
            _logger.exception(e)
            raise ValueError(errors['FF'].format(os.path.basename(
                self.fastqfile)))


class CheckFastq(object):
    """Check fastq file."""

    header = {
        'base_count': 0, 'read_count': 0, 'phreq_set': '', 'pair_error': '',
        'file1_read_count': 0, 'file1_base_count': 0, 'file1_error': '',
        'file2_read_count': 0, 'file2_base_count': 0, 'file2_error': ''}

    def __init__(self, fastq1, fastq2=None, dofast=10):
        """Init class."""
        self.fastq1 = fastq1
        self.fastq2 = fastq2
        self._run_fastq(int(dofast))

    def _run_fastq(self, dofast):
        """Run fastq."""
        file1error = errors['FF'].format(os.path.basename(self.fastq1))
        iters = [ReadFastq(self.fastq1)]
        if self.fastq2 is None:
            self.hold = HoldSingle()
        else:
            self.hold = HoldPair()
            file2error = errors['FF'].format(os.path.basename(self.fastq2))
            iters.append(ReadFastq(self.fastq2))
        try:
            i = 0
            read = None
            for tmp in zip_longest(*iters):
                if len(tmp) == 2:
                    read = PairRead(i, tmp[0], tmp[1])
                else:
                    read = SingleRead(i, tmp[0])
                self.hold.add(read)
                i += 1
                if i == 0 or i % dofast == 0:
                    if self.hold.check_error(read):
                        break
            if i % dofast != 0:
                self.hold.check_error(read)
        except ValueError as e:
            if str(e).startswith(file1error):
                if self.fastq2 is None:
                    self.hold.error = file1error
                else:
                    self.hold.read1.error = file1error
            elif self.fastq2 is not None and str(e).startswith(file2error):
                self.hold.read2.error = file2error
            else:
                raise
        if self.fastq2 is not None:
            self.hold.cal()

    @lazypropery
    def check_dict(self):
        """Return dict."""
        adict = deepcopy(self.header)
        for key, value in adict.items():
            if key.startswith(('file1_', 'file2_')):
                if key.startswith('file1_'):
                    key1 = key.replace('file1_', '')
                    if self.fastq2 is None:
                        adict[key] = getattr(self.hold, key1, value)
                    else:
                        adict[key] = getattr(self.hold.read1, key1, value)
                else:
                    if self.fastq2 is not None:
                        key1 = key.replace('file2_', '')
                        adict[key] = getattr(self.hold.read2, key1, value)
            else:
                adict[key] = getattr(self.hold, key, value)
        return adict


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('fastq1', help='fastq1 path')
    parser.add_argument('-f', '--fastq2', help='fastq2 path')
    parser.add_argument('-r', '--run',
                        help='run by times, default is %(default)s',
                        default=1)
    args = parser.parse_args()
    sys.stdout.write('='*20)
    sys.stdout.write('\n')
    sys.stdout.write('Start time: %s' % time.asctime(time.localtime(
        time.time())))
    sys.stdout.write('\n')
    checkfastq = CheckFastq(args.fastq1, args.fastq2, args.run)
    sys.stdout.write('%s' % json.dumps(checkfastq.check_dict))
    sys.stdout.write('\n')
    sys.stdout.write('End time: %s' % time.asctime(time.localtime(
        time.time())))
    sys.stdout.write('\n')
