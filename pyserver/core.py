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
from functools import wraps


app = Flask(__name__)
app.config['VERSION'] = os.environ.get('CURRENT_SHA', None)
app.config['X-HOSTNAME'] = os.environ.get('XHOSTNAME', '')

def make_my_response_json(f):
    @wraps(f)
    def view_wrapper(*args, **kwargs):
        return json_response(**f(*args, **kwargs))
    return view_wrapper

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

def global_response_handler(response):
    response.headers['X-HOSTNAME'] = app.config['X-HOSTNAME']
    return response

app.process_response = global_response_handler    

@app.route("/diagnostic", methods=["GET"])
@make_my_response_json
def diagnostic_view():
    return dict(message="ok", version=app.config['VERSION'])

@app.route("/diagnostic/echo", methods=["GET"])
@make_my_response_json
def diagnostic_echo_view():
    d = request.values.to_dict()
    if 'callback' in d:
        del(d['callback'])
    return d

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
