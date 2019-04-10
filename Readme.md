# 常用的python工具包
## Dir_File
处理文件和目录的相应Python工具包。
### 解压文件
1. 脚本路径：`./Dir_File/decompress.py`
2. 使用方法：
```
python ./Dir_File/decompress.py infile outpath
```
3. 备注：目前仅支持解压\*.tar.gz, \*.gz, \*.zip, \*.tar, \*.rar文件。

### 测试压缩文件完整性
1. 脚本路径：`./Dir_File/check_compress.py`
2. 使用方法：
```
CheckCompress:
    check: 检查压缩文件。
```
3. 备注：目前仅支持检查\*.gz, \*.zip文件。

### 检查文件md5或者生成文件md5
1. 脚本路径：`./Dir_File/file_md5.py`
2. 使用方法：
```
FileMD5:
    md5: 获取MD5信息。
    write_md5: 将MD5信息输出到文件。
md5sum: 检查文件的MD5是否和md5文件一致。
```
### 忽略“Ignore Gzip Trailing Garbage Data in Python”这种错误
1. 脚本路径：`./Dir_File/altgzip.py`
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

## NGS
