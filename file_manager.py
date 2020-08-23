import hashlib
import os


def get_hash(path: str, offset: int, length: int = None) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        f.seek(offset)
        if length is None:
            return hashlib.sha256(f.read()).hexdigest()
        else:
            return hashlib.sha256(f.read(length)).hexdigest()


def get_data(path: str, offset: int, length: int) -> bytes:
    if not os.path.exists(path):
        return b""
    with open(path, "rb") as f:
        f.seek(offset)
        return f.read(length)


def get_file_size(path: str) -> int:
    if not os.path.exists(path):
        return 0
    return os.lstat(path).st_size


def write_data(path: str, offset: int, data: bytes):
    if not os.path.exists(path):
        with open(path, "w"):
            pass

    with open(path, "r+b") as f:
        f.seek(offset)
        f.write(data)


def testando():
    fsize = get_file_size("a.mp4")
    length = fsize // 4
    for i in range(4):
        offset = i * length
        if get_hash("a.mp4", offset, length) != get_hash("b.mp4", offset, length):
            print("Writting")
            write_data("b.mp4", offset, get_data("a.mp4", offset, length))
        else:
            print("No need")


# print(get_hash("dwn.txt", 0, 10))
# write_data("dwn.txt", 1024 * 1024, b"")
# print(get_hash("up.txt", 0, 10))
# print(get_hash("dwn.txt", 1024 * 1024, 10))
# f.seek(0)
# f.write(b"hehe")
if __name__ == "__main__":
    testando()
