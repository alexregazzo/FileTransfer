import os
import hashlib
from contextlib import contextmanager
import typing
import requests
import math


class File:
    endpoint_domain = "http://127.0.0.1:8080/"
    endpoint_file_info = "fileinfo?fpath={fpath}"
    endpoint_download_data = "getdata?fpath={fpath}&offset={offset}&length={length}"
    endpoint_check_hash = "gethash?fpath={fpath}&offset={offset}&length={length}"
    endpoint_list_files = "listfiles?dpath={dpath}"

    def __init__(self, fpath: str, *, saveas: str = None):
        self.fpath = fpath
        if saveas is None:
            self.saveas = self.fpath
        else:
            self.saveas = saveas
        self._size = None
        self._download_size = None

    def get_file_info_url(self) -> str:
        return self.endpoint_domain + self.endpoint_file_info.format(fpath=self.fpath)

    def get_download_data_url(self, *, offset: int = 0, length: int = None) -> str:
        return self.endpoint_domain + self.endpoint_download_data.format(fpath=self.fpath, offset=offset, length=(length if length is not None else ""))

    def get_check_hash_url(self, *, offset: int = 0, length: int = None) -> str:
        return self.endpoint_domain + self.endpoint_check_hash.format(fpath=self.fpath, offset=offset, length=(length if length is not None else ""))

    @classmethod
    def get_list_files_url(cls, *, dpath: str) -> str:
        return cls.endpoint_domain + cls.endpoint_list_files.format(dpath=dpath)

    @property
    def exists(self) -> bool:
        return os.path.exists(self.saveas)

    def yield_file_bytes_chunks(self, *, offset: int = 0, length: int = None, chunk_size: int = 1048576) -> bytes:
        bytes_read = 0
        read_bytes_amount = length if length is not None else self.size - offset
        if self.exists:
            with open(self.saveas, "rb") as f:
                f.seek(offset)
                while bytes_read < read_bytes_amount:
                    yield f.read(chunk_size)
                    bytes_read += chunk_size

    def get_hash(self, *, offset: int = 0, length: int = None, chunk_size: int = 10485760) -> str:
        m = hashlib.sha256()
        for chunk in self.yield_file_bytes_chunks(offset=offset, length=length, chunk_size=chunk_size):
            m.update(chunk)
        return m.hexdigest()

    def get_download_file_hash(self, offset: int = 0, length: int = None) -> str:
        return requests.get(self.get_check_hash_url(offset=offset, length=length)).text

    @property
    def size(self) -> int:
        if self._size is None:
            if self.exists:
                self._size = os.stat(self.saveas).st_size
            else:
                return 0
        return self._size

    @contextmanager
    def write_data(self, *, offset: int = 0) -> typing.BinaryIO:
        if not self.exists:
            with open(self.saveas, "w"):
                pass
        with open(self.saveas, "r+b") as f:
            f.seek(offset)
            try:
                yield f
            finally:
                f.close()

    def get_download_file_size(self) -> int:
        if self._download_size is None:
            self._download_size = requests.get(self.get_file_info_url()).json()["size"]
        return self._download_size

    @staticmethod
    def display(percentage: float) -> None:
        display_size = 50
        print(F"""\r[{"=" * math.floor(percentage * display_size)}{" " * math.ceil(display_size - percentage * display_size)}] {round(percentage * 10000) / 100}%""", end='')

    def download_data(self, *, offset: int = 0, length: int = None, chunk_size: int = 1048576) -> None:
        fsize = self.get_download_file_size()
        with requests.get(self.get_download_data_url(offset=offset, length=length), stream=True) as r:
            if not self.exists:
                with open(self.saveas, "w"):
                    pass
            with open(self.saveas, 'r+b') as f:
                f.seek(offset)
                current = offset
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    current += len(chunk)
                    self.display(current / fsize)

    def download(self):
        offset = self.get_missing_part_offset()
        self.download_data(offset=offset)

    def get_missing_part_offset(self, chunk_size: int = 1048576) -> int:
        if self.exists:
            for i in range(self.get_download_file_size() // chunk_size):
                print(f"Checking {i}: offset={i * chunk_size} and length={chunk_size}")
                if self.get_hash(offset=i * chunk_size, length=chunk_size) != self.get_download_file_hash(offset=i * chunk_size, length=chunk_size):
                    print("Not good, downloading from here")
                    offset = i * chunk_size
                    return offset
                else:
                    print("Good")
            return self.size
        else:
            return 0


if __name__ == "__main__":
    File("a.mp4", saveas="c.mp4").download()
