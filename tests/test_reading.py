import tempfile
import unittest
import pathlib
import zipfile

try:
    from sozipfile import sozipfile
except ImportError:
    import sys

    sys.path.append("../sozipfile")
    from sozipfile import sozipfile


class TestReading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create temporary directory
        cls._tempdir = tempfile.TemporaryDirectory(prefix="test-sozipfile-")
        cls.addClassCleanup(cls._tempdir.cleanup)
        cls.temp_path = pathlib.Path(cls._tempdir.name)
        # create archives with sozipfile and zipfile
        cls.sozip_path = cls.temp_path / "soarchive.zip"
        cls.content = "\n".join(f"{number:04d}" for number in range(5000)).encode()
        cls.chunk_size = 1024
        with sozipfile.ZipFile(
            cls.sozip_path,
            "w",
            compression=sozipfile.ZIP_DEFLATED,
            chunk_size=cls.chunk_size,
        ) as myzip:
            myzip.writestr("numbers.txt", cls.content)
            # write an uncompressed file
            myzip.writestr(
                "hello.txt", "Hello World!", compress_type=sozipfile.ZIP_STORED
            )
        # create conventional zip archive
        cls.zip_path = cls.temp_path / "archive.zip"
        with zipfile.ZipFile(
            cls.zip_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as myzip:
            myzip.writestr("numbers.txt", cls.content)

    def test_read_conventional_zip_with_sozipfile(self):
        with sozipfile.ZipFile(self.zip_path, mode="r") as myzip:
            zinfo = myzip.getinfo("numbers.txt")
            self.assertIsNone(zinfo.sozip_index)
            with myzip.open(zinfo) as file:
                content = file.read()
            self.assertEqual(content, self.content)

    def test_read_seek_optimized_zip_with_sozipfile(self):
        with sozipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            # read un-indexed file
            zinfo = myzip.getinfo("hello.txt")
            self.assertIsNone(zinfo.sozip_index)
            with myzip.open(zinfo) as file:
                hello = file.read()
            self.assertEqual(hello, b"Hello World!")
            # read indexed file
            zinfo = myzip.getinfo("numbers.txt")
            self.assertIsNotNone(zinfo.sozip_index)
            with myzip.open(zinfo) as file:
                content = file.read()
        self.assertEqual(content, self.content)

    def test_seek_and_read(self):
        with sozipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            with myzip.open("numbers.txt") as file:
                file.seek(2000)
                content = file.read(1500)
        self.assertEqual(content, self.content[2000:3500])

    def test_seek_before_file(self):
        with sozipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            with myzip.open("numbers.txt") as file:
                file.seek(-2 * self.chunk_size)
                content = file.read(100)
        self.assertEqual(content, self.content[:100])
        # check that zipfile behaves the same
        with zipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            with myzip.open("numbers.txt") as file:
                file.seek(-2 * self.chunk_size)
                content = file.read(100)
        self.assertEqual(content, self.content[:100])

    def test_seek_beyond_filesize(self):
        with sozipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            with myzip.open("numbers.txt") as file:
                file.seek(len(self.content) + 500)
                content = file.read(100)
        self.assertEqual(content, b"")
        # check that zipfile behaves the same
        with zipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            with myzip.open("numbers.txt") as file:
                file.seek(len(self.content) + 500)
                content = file.read(100)
        self.assertEqual(content, b"")

    def test_reactivate_crc_check(self):
        with sozipfile.ZipFile(self.sozip_path, mode="r") as myzip:
            zinfo = myzip.getinfo("numbers.txt")
            zinfo.CRC += 1
            with myzip.open("numbers.txt") as file:
                file.seek(-500, 2)
                file.read()  # no exception
                file.seek(0)
                with self.assertRaisesRegex(
                    sozipfile.BadZipFile, r"Bad CRC-32 for file .*"
                ):
                    file.read()
