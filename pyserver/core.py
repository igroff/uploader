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
from argparse import ArgumentParser


app = Flask(__name__)
VERSION = os.environ.get('CURRENT_SHA', None)

def json_response(*args, **kwargs):
    """ creates a response assuming that the provided thing is either a 
        dictionary object or a JSON string.  Handles the setting of content type
        and propery callback wrapping for JSONP handling
    """
    callback = request.values.get('callback', None)
    if args:
        response_string = args[0]
    else:
        response_string = json.dumps(kwargs)

    if callback:
        response_string = "%s(%s);" % (callback, response_string)
        
    return response_string, 200, {"Content-Type": "application/json"}
    

@app.route("/diagnostic", methods=["GET"])
def diagnostic_view():
    return json_response(message="ok", version=VERSION)

execfile('./handlers.py')


if (__name__ == "__main__"):
    """ we should only get here for debugging, as we're gonna use gunicorn
        for serving in production
    """
    arg_parser = ArgumentParser(description="")
    arg_parser.add_argument("-p", "--port", default=5000, type=int)
    arg_parser.add_argument("action", choices=('start', 'test'))
    args = arg_parser.parse_args()
    if args.action == "start":
        app.run(use_reloader=True, debug=True, use_debugger=True, port=args.port)
    else:
        import unittest
        import sys
        execfile("./tests.py")
        # unittest uses command line params, so remove ours
        sys.argv.pop()
        unittest.main() 
