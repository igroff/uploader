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
VERSION = os.environ.get('CURRENT_SHA', None)

@app.route("/diagnostic", methods=["GET"])
def diagnostic_view():
    return jsonify(message="ok", version=VERSION)

if (__name__ == "__main__"):
    """ we should only get here for debugging, as we're gonna use gunicorn
        for serving in production
    """
    app.run(use_reloader=True, debug=True, use_debugger=True, port=PORT)
