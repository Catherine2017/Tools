<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

- [常用的python工具包](#常用的python工具包)
	- [Dir_File](#dirfile)
		- [解压文件](#解压文件)
		- [测试压缩文件完整性](#测试压缩文件完整性)
		- [检查文件md5或者生成文件md5](#检查文件md5或者生成文件md5)
		- [忽略“Ignore Gzip Trailing Garbage Data in Python”这种错误](#忽略ignore-gzip-trailing-garbage-data-in-python这种错误)
		- [读取gz和bz2压缩文件（gz文件能忽略“decompression OK, trailing garbage ignored”）](#读取gz和bz2压缩文件gz文件能忽略decompression-ok-trailing-garbage-ignored)
	- [NGS](#ngs)

<!-- /TOC -->
# 常用的python工具包
## Dir_File
处理文件和目录的相应Python工具包。
### 解压文件
1. 脚本路径：`./script/decompress.py`
2. 使用方法：
```
python ./script/decompress.py infile outpath
```
3. 备注：目前仅支持解压\*.tar.gz, \*.gz, \*.zip, \*.tar, \*.rar文件。

### 测试压缩文件完整性
1. 脚本路径：`./script/check_compress.py`
2. 使用方法：
```
CheckCompress:
    check: 检查压缩文件。
```
3. 备注：目前仅支持检查\*.gz, \*.zip, \*.bz2文件。

### 检查文件md5或者生成文件md5
1. 脚本路径：`./script/file_md5.py`
2. 使用方法：
```
FileMD5:
    md5: 获取MD5信息。
    write_md5: 将MD5信息输出到文件。
md5sum: 检查文件的MD5是否和md5文件一致。
```
### 忽略“Ignore Gzip Trailing Garbage Data in Python”这种错误
1. 脚本路径：`./script/altgzip.py`
2. 使用方法：
```
>>> import altgzip
>>> with altgzip.AltGzipFile('trailing-garbage.gz') as gz:
...     data = gz.read()
...
decompression OK, trailing garbage ignored
>>> len(data)
36
```

### 读取gz和bz2压缩文件（gz文件能忽略“decompression OK, trailing garbage ignored”）
1. 脚本路径：`./script/read_gzbzfile.py`
2. 使用方法：
```
>>> import ReadGgBz2
>>> rg = ReadGgBz2('test.gz')
>>> for line in rg:
        pass
```
3. 备注：仅能读取gz和bz2文件。

## NGS
