import requests
import file_manager
import os
import typing
import re

ENDPOINT = "http://127.0.0.1:8080/"


def get_file_info(path: str) -> dict:
    return requests.get(F"""{ENDPOINT}fileinfo?path={path}""").json()


def check_file(path: str, saveas: str, offset: int = 0, length: int = None) -> bool:
    filehash = file_manager.get_hash(saveas, offset, length)
    response = requests.get(F"""{ENDPOINT}gethash?path={path}&offset={offset}&length={length}""")
    return response.text == filehash


def download_data(path: str, saveas: str, offset: int = 0, length: int = None):
    fsize = get_file_info(path)["size"]
    with requests.get(F"""{ENDPOINT}getdata?path={path}&offset={offset}{f"&length={length}" if length is not None else ""}""", stream=True) as r:
        if not os.path.exists(saveas):
            with open(saveas, "w"):
                pass
        with open(saveas, 'r+b') as f:
            f.seek(offset)
            current = offset
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                current += len(chunk)
                print(current / fsize)


def download_file(path: str, saveas: str):
    print(f"Download file '{path}' saving as '{saveas}'")
    if os.path.exists(saveas):
        print("Path exists")
        if check_file(path, saveas):
            # file is ok
            print("File is ok")
            return
        else:
            # file not ok
            print("File is not ok")
            fileinfo = get_file_info(path)
            length = 1024 * 1024
            for i in range(fileinfo['size'] // length):
                print(f"Checking {i}: offset={i * length} and length={length}")
                if not check_file(path, saveas, i * length, length):
                    print("Not good, downloading from here")
                    offset = i * length
                    download_data(path, saveas, offset)
                    break
                else:
                    print("Good")
    else:
        # file not exist
        print("File doesnt exist, downloading")
        download_data(path, saveas)


def get_files_list() -> typing.List[str]:
    return requests.get(F"""{ENDPOINT}listfiles""").json()


def main():
    global ENDPOINT
    ENDPOINT = f"""http://{input("Type in the ip address: ")}:8080/"""
    while True:
        try:
            print("*" * 50)
            regularexpression = input("Enter the regular expression: ")
            download_files = []
            all_files = get_files_list()
            for file in all_files:
                if re.fullmatch(regularexpression, file, re.IGNORECASE):
                    download_files.append(file)

            print("-" * 50)

            for file in download_files:
                print(file)

            if input("Would you like to download these files[y/n]:").lower() == "y":
                break
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("Erro:", e)
    for file in download_files:
        download_file(file, file)


if __name__ == "__main__":
    main()
# os.makedirs("TesteArquivos", exist_ok=True)
# os.chdir("TesteArquivos")
# download_file("a.mp4", "b.mp4")
