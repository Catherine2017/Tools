"""

Get base count and error for fastq file both single end and pair end
sequencing.

"""

from itertools import zip_longest
import logging
import os
import re
import sys

_logger = logging.getLogger(__name__)


class CheckFastq(object):
    """Get base count and error for fastq file."""

    pair = ['read1', 'read2']
    compressed = ('.gz', '.bz2')
    phredrange = (33, 126)
    phredQ = (58, 75)
    single_errors = [
        'The [{}] line:({}) have wrong base',
        'The [{}] line:({}) is not {}',
        ('The 4th line length {} is not equal to the 2nd line length {}'
         ' at 4th line [{}]'),
        'The file don\'t have an integral multiple of 4 number of lines',
        'The ord of qualiyty ({0}-{1}) is out of {2[0]}-{2[1]} at line [{3}]',
        'Failed to read compressed file: {}.',
        'Failed to deal fastq.']
    pair_errors = [
        'Read1 name ({}) is not same with read2 name ({}) at line [{}]',
        'Read1 number is not equal to read2 number.']
    readname_normal = re.compile(r'\/[12]$')
    readname_454 = re.compile(r'\.[fr]$')
    casava_1_8 = re.compile(
        r'^@([a-zA-Z0-9_-]+:\d+:[a-zA-Z0-9_-]+:\d+:\d+:[0-9-]+:'
        '[0-9-]+)(\s+|\:)([12]):[YN]:\d*[02468]:?([ACGTN\_\+\d+]*)$')

    # 参考资料：
    # https://en.wikipedia.org/wiki/FASTQ_format
    # https://ena-docs.readthedocs.io/en/latest/format_01.html#other-read-data
    # https://github.com/nunofonseca/fastq_utils/wiki/FASTQ-validation

    def set_value(self, filepath, pair_index):
        """Init value."""
        header = {'base_count': 0, 'read_count': 0, 'error': '',
                  'line2_len': 0, 'line4_len': 0, 'line_count': 0,
                  'phredq': ""}
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

    def read_file(self, read1file, read2file=""):
        """Read file."""
        def read_singlefile(filepath):
            iterl = None
            if not filepath:
                return iterl
            if filepath.endswith(self.compressed):
                from read_gzbzfile import ReadGgBz2
                iterl = ReadGgBz2(filepath)
            else:
                iterl = open(filepath, 'rt')
            return iterl

        def close_singlefile(iterl, filepath):
            if iterl is not None and not filepath.endswith(self.compressed):
                iterl.clse()

        self.base_count = 0
        self.read_count = 0
        self.phredq = ""
        self.read1file = self.set_value(read1file, 0)
        self.read2file = self.set_value(read2file, 1)
        iter1 = read_singlefile(self.read1file)
        iter2 = read_singlefile(self.read2file)
        check = True
        try:
            check = self.read_iter(iter1, iter2)
        except Exception as e:
            _logger.exception(e)
            self.check_file(self.read1file, 'read1')
            self.check_file(self.read2file, 'read2')
            check = False
        finally:
            close_singlefile(iter1, self.read1file)
            close_singlefile(iter2, self.read2file)
        return check

    def check_file(self, filepath, readname):
        """Check file is wrong compressed."""
        if not filepath or not os.path.isfile(filepath):
            return True
        from check_compress import CheckCompress
        if filepath.endswith(self.compressed):
            cc = CheckCompress(filepath)
            if not cc.check():
                self.__dict__['%s_error' % (readname)] = \
                        self.single_errors[5].format(cc.error)
                return True
        self.__dict__['%s_error' % (readname)] =  self.single_errors[6]
        return True

    def check_error(self):
        """Check whether has error."""
        errorlist = ['read1_error', 'read2_error', 'pair_error']
        tag = False
        for tmp in errorlist:
            if hasattr(self, tmp) and getattr(self, tmp):
                tag = True
                break
        return tag

    def check_firstword(self, i, line, a):
        """Check line [0] is a."""
        error = ""
        if line[0] != a:
            error = self.single_errors[1].format(i, line, a)
        return error

    def check_lines(self, i, lines):
        """Check lines."""
        defi = (i + 1) % 4
        if lines:
            lines_notNone = len([x for x in lines if x is not None])
            origread, readnames = [], []
            errors = []
            for j, line in enumerate(lines):
                if line is None:
                    continue
                self.__dict__['%s_line_count' % self.pair[j]] += 1
                length = len(line)
                error = ''
                if defi == 1:
                    # single pair 检查是否“@”开头
                    error = self.check_firstword(i, line, '@')
                    self.__dict__['%s_line2_len' % self.pair[j]] = 0
                    self.__dict__['%s_line4_len' % self.pair[j]] = 0
                    if lines_notNone > 1:
                        origread.append(line)
                        # 针对某些BGI文件，文件名称如
                        # “@CL100066606L2C001R002_528666#162_967_615/1
                        #     1       1”
                        readnametmp = line.split('\t')[0]
                        if self.readname_normal.search(readnametmp):
                            readnames.append(self.readname_normal.sub(
                                '', readnametmp))
                        elif self.readname_454.search(readnametmp):
                            readnames.append(self.readname_454.sub(
                                '', readnametmp))
                        elif self.casava_1_8.search(readnametmp):
                            match = self.casava_1_8.search(readnametmp)
                            readnames.append(match.group(1))
                        else:
                            readfile = getattr(self, '%sfile' % self.pair[j])
                            _logger.warning(
                                "New pattern readname:%s in file:%s!",
                                readnametmp, readfile)
                            readnames.append(readnametmp)
                elif defi == 2:
                    # 计算read和base数目
                    self.__dict__['%s_read_count' % self.pair[j]] += 1
                    self.__dict__['%s_base_count' % self.pair[j]] += length
                    # 获取每单元碱基长度
                    self.__dict__['%s_line2_len' % self.pair[j]] = length
                    line = line.upper()
                    # 检查碱基是否为ATCGN，0123针对454测序
                    if not set(line).issubset(set('ATCGN0123')):
                        error = self.single_errors[0].format(i, line)
                elif defi == 3:
                    # 检查第三行是否为“+”开头
                    error = self.check_firstword(i, line, '+')
                elif defi == 0:
                    # 获取质量值体系
                    phredq = getattr(self, '%s_phredq' % self.pair[j])
                    phredset = set(map(ord, line))
                    amin = min(phredset)
                    amax = max(phredset)
                    if amin <= self.phredQ[0]:
                        phredq = '33'
                    elif amax >= self.phredQ[1]:
                        phredq = '64'
                    self.__dict__['%s_phredq' % self.pair[j]] = phredq
                    # 检查质量值长度是否和碱基长度一致
                    self.__dict__['%s_line4_len' % self.pair[j]] = length
                    line2_len = getattr(
                        self, '%s_line2_len' % self.pair[j])
                    if line2_len != length:
                        error = self.single_errors[2].format(
                            length, line2_len, i)
                    # 检查质量值是否在Phred范围33, 126
                    if amin < self.phredrange[0] or amax > self.phredrange[1]:
                        error = self.single_errors[4].format(
                            amin, amax, self.phredrange, i)
                if error:
                    self.__dict__['%s_error' % self.pair[j]] = error
                    errors.append(error)
            if lines_notNone > 1:
                if defi == 1:
                    if len(set(readnames)) != 1:
                        self.pair_error = self.pair_errors[0].format(
                            origread[0], origread[1], i)
            if any(errors) or (hasattr(self, 'pair_error') and
                               self.pair_error):
                return False
        return True

    def read_iter(self, iter1, iter2=None):
        """Run function."""
        iter_args = [iter1]
        if iter2 is not None:
            iter_args.append(iter2)
            self.pair_error = ''
        for i, lines in enumerate(zip_longest(*iter_args)):
            if not self.check_lines(i, lines):
                break
        else:
            if iter2 is not None:
                # 检查read1和read2数目是否一致
                if self.read1_read_count != self.read2_read_count:
                    self.pair_error = self.pair_errors[1]
            for read in self.pair:
                # 检查行数是否为4的倍数
                key = '%s_line_count' % read
                if hasattr(self, key):
                    value = getattr(self, key) % 4
                    if value != 0:
                        setattr(self, '%s_error' % read, self.single_errors[3])
        if self.check_error():
            return False
        else:
            # 获取总体的统计数据
            total_stat = ['base_count', 'read_count', 'phredq']
            for astat in total_stat:
                for readname in self.pair:
                    key = '%s_%s' % (readname, astat)
                    if hasattr(self, key):
                        attrtmp = getattr(self, key)
                        if astat == 'phredq':
                            if attrtmp:
                                self.__dict__[astat] = attrtmp
                        else:
                            self.__dict__[astat] += attrtmp
            return True


def test():
    """Test for module."""
    import time
    if len(sys.argv) < 2:
        print('Usage: python {0} read1.fq.gz [read2.fq.gz]'.format(
            sys.argv[0]))
        sys.exit(0)
    print('=' * 24)
    print('start time:', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    cf = CheckFastq()
    cf.read_file(*sys.argv[1:])
    print('-'*6, 'total statistics', '-'*6)
    print('total base count:', cf.base_count)
    print('total read count:', cf.read_count)
    print('phred range:', cf.phredq)
    single_info = ['base_count', 'read_count', 'error', 'phredq']
    for read in cf.pair:
        print('-'*6, read, 'information', '-'*6)
        for tmp in single_info:
            key = '%s_%s' % (read, tmp)
            if hasattr(cf, key):
                print('%s:%s' % (key, getattr(cf, key)))
    if hasattr(cf, 'pair_error'):
        print('-'*6, 'pair error', '-'*6)
        print('pair error:', cf.pair_error)
    print('end time:', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


if __name__ == '__main__':
    test()
