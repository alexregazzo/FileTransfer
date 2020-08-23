from flask import Flask, request, Response
import json
import file_manager
import os

app = Flask(__name__)
videos_folder = "D:/Users/Alex/Videos"


@app.route("/fileinfo")
def fileinfo():
    try:
        path = request.args["path"]
    except KeyError:
        return b""
    path = os.path.join(videos_folder, path)
    return json.dumps({
        "size": file_manager.get_file_size(path)
    })


@app.route("/gethash")
def gethash():
    try:
        offset = int(request.args.get("offset", ""))
    except ValueError:
        offset = 0
    else:
        if offset < 0:
            offset = 0

    try:
        length = int(request.args.get("length", ""))
    except ValueError:
        length = None
    else:
        if length < 0:
            length = 0

    try:
        path = request.args["path"]
    except KeyError:
        return b""
    path = os.path.join(videos_folder, path)

    return file_manager.get_hash(path, offset, length)


@app.route("/listfiles")
def listfiles():
    return json.dumps(os.listdir(videos_folder))


@app.route("/getdata")
def getdata():
    try:
        offset = int(request.args.get("offset", ""))
    except ValueError:
        offset = 0
    else:
        if offset < 0:
            offset = 0

    try:
        length = int(request.args.get("length", ""))
    except ValueError:
        length = None
    else:
        if length < 0:
            length = 0

    try:
        path = request.args["path"]
    except KeyError:
        return b""

    path = os.path.join(videos_folder, path)

    with open(path, "rb") as f:
        f.seek(offset)
        if length is not None:
            return Response(f.read(length))
        else:
            return Response(f.read())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
