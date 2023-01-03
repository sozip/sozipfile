# sozipfile

sozipfile is a fork of Python [zipfile](https://docs.python.org/3/library/zipfile.html)
module, from its implementation in CPython 3.11, which implements the
[SOZip](https://sozip.org) optimization,
when writing deflate compressed files whose size exceeds the chunk size (defaults
to 32768 bytes)

Example to generate a SOZip-optimized file:

```python
import sozipfile.sozipfile as zipfile
with zipfile.ZipFile('my.zip', 'w',
                     compression=zipfile.ZIP_DEFLATED,
                     chunk_size=zipfile.SOZIP_DEFAULT_CHUNK_SIZE) as myzip:
    myzip.write('my.file')
```

Example to check if a file within a ZIP is SOZip-optimized:

```python
import sozipfile.sozipfile as zipfile
with zipfile.ZipFile('my.zip', 'r') as myzip:
    if myzip.getinfo('my.gpkg').is_sozip_optimized(myzip):
        print('SOZip optimized!')
```

Note: use of the SOZip index is not currently implemented in the read side, for now.

Available on [pypi](https://pypi.org/project/sozipfile):
```shell
pip install sozipfile
```
