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
    """ Creates a JSON response for the given params, handling the creation a callback wrapper
        if a callback is provided, and allowing for either a string arg (expected to be JSON)
        or kwargs to be passed formatted correctly for the response.
        Also sets the Content-Type of the response to application/json
    """
    # if provided, use the status code otherwise default to 200
    status_code = kwargs.get('status_code', 200)
    # remove it so it doesn't end up in our response
    if 'status_code' in kwargs:
        del(kwargs['status_code'])

    if args:
        response_string = args[0]
    else:
        response_string = json.dumps(kwargs)

    callback = request.values.get('callback', None)
    if callback:
        response_string = "%s(%s);" % (callback, response_string)
        
    return response_string, status_code, {"Content-Type": "application/json"}
    

@app.route("/diagnostic", methods=["GET"])
def diagnostic_view():
    return json_response(status_code=200, message="ok", version=VERSION)

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
