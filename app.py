from flask import Flask, request, Response
import json
import os
from archive import File

app = Flask(__name__)
videos_folder = "D:/Users/Alex/Videos"


@app.route("/fileinfo")
def fileinfo():
    try:
        fpath = request.args["fpath"]
    except KeyError:
        return b""

    return json.dumps({
        "size": File(fpath).size
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
        fpath = request.args["fpath"]
    except KeyError:
        return b""

    return File(fpath).get_hash(offset=offset, length=length)


@app.route("/listfiles")
def listfiles():
    try:
        dpath = request.args["dpath"]
    except KeyError:
        return b""
    return json.dumps(os.listdir(dpath))


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
        fpath = request.args["fpath"]
    except KeyError:
        return b""

    return Response(File(fpath).yield_file_bytes_chunks(offset=offset, length=length))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
