import os
import sys
sys.path.append("../sozipfile")
import sozipfile.sozipfile as zipfile

this_dir = os.path.dirname(__file__)

def test_basic():
    out_zip = this_dir + '/test.zip'
    try:
        with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, chunk_size=128) as myzip:
            myzip.write(this_dir + '/test_sozipfile.py', arcname='foo.py')
            myzip.writestr('baz.py', "foo")
            myzip.write(this_dir + '/test_sozipfile.py', arcname='subdir/bar.py')

        # Very basic check...
        zip_raw = open(out_zip, 'rb').read()
        assert b'.foo.py.sozip.idx' in zip_raw
        assert b'.baz.py.sozip.idx' not in zip_raw
        assert b'subdir/.bar.py.sozip.idx' in zip_raw

        with zipfile.ZipFile(out_zip, 'r') as myzip:
            assert myzip.namelist() == ['foo.py', 'baz.py', 'subdir/bar.py']
            assert myzip.read('foo.py') == open(this_dir + '/test_sozipfile.py', 'rb').read()
            assert myzip.read('baz.py') == b"foo"
            assert myzip.read('subdir/bar.py') == open(this_dir + '/test_sozipfile.py', 'rb').read()

            assert myzip.getinfo('foo.py').is_sozip_optimized(myzip)
            assert not myzip.getinfo('baz.py').is_sozip_optimized(myzip)
            assert myzip.getinfo('subdir/bar.py').is_sozip_optimized(myzip)

    finally:
        if os.path.exists(out_zip):
            os.unlink(out_zip)
