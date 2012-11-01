#! /usr/bin/env python
import os
import uuid
import json
import time
import shutil
import logging
from os import path

from flask import Flask, request, redirect, url_for
from flask import render_template, jsonify
from flask import Response


app = Flask(__name__)
PORT = os.environ.get('FLASK_PORT', 5000)
DEBUG = os.environ.get('FLASK_DEBUG', False)
VERSION = os.environ.get('CURRENT_SHA', None)
USE_RELOADER = DEBUG or os.environ.get('FLASK_RELOAD', False)

@app.route("/diagnostic", methods=["GET"])
def diagnostic_view():
    return jsonify(message="ok", version=VERSION)

print("USE_RELOADER=%s" % USE_RELOADER)
print("DEBUG=%s" % DEBUG)

if (__name__ == "__main__"):
    app.run(
        debug=DEBUG,
        use_debugger=DEBUG,
        port=PORT,
        use_reloader=USE_RELOADER
    )
